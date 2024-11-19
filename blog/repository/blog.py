from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from typing import Optional, List

def get_user_gallery(db: Session, user_id: int) -> List[schemas.ShowPhoto]:
    photos = db.query(models.Photo).filter(models.Photo.user_id == user_id).all()
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found for the user.")
    return photos

def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs

def sort_blogs_by_length(db: Session, sort_order: Optional[str] = None) -> List[schemas.ShowBlogWithLength]:
    if sort_order not in [None, "asc", "desc"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sort order. Use 'asc', 'desc', or omit it.")

    if sort_order == "asc":
        blogs = db.query(models.Blog).order_by(func.length(models.Blog.body)).all()
    elif sort_order == "desc":
        blogs = db.query(models.Blog).order_by(func.length(models.Blog.body).desc()).all()
    else:
        blogs = db.query(models.Blog).all()  
    
    # Формируем список результатов с длиной текста
    result = []
    for blog in blogs:
        length = len(blog.body)  
        result.append({
            "id": blog.id,
            "title": blog.title,
            "body": blog.body,
            "creator": blog.creator,
            "length": length  
        })

    return result

def blogs_sorted_by_comments(db: Session, sort_order: Optional[str] = None) -> List[schemas.ShowBlogWithCommentCount]:
    # Запрос для получения блогов с подсчетом комментариев
    if sort_order == "asc":
        blogs = db.query(models.Blog).outerjoin(models.Comment).group_by(models.Blog.id).order_by(func.count(models.Comment.id).asc()).all()
    elif sort_order == "desc":
        blogs = db.query(models.Blog).outerjoin(models.Comment).group_by(models.Blog.id).order_by(func.count(models.Comment.id).desc()).all()
    else:
        blogs = db.query(models.Blog).outerjoin(models.Comment).group_by(models.Blog.id).all()

    # Формируем список результатов
    result = []
    for blog in blogs:
        comment_count = db.query(func.count(models.Comment.id)).filter(models.Comment.blog_id == blog.id).scalar()
        result.append({
            "id": blog.id,
            "title": blog.title,
            "body": blog.body,
            "creator": blog.creator,
            "comment_count": comment_count 
        })

    return result
def blogs_sorted_by_moderated_comments(db: Session, sort_order: Optional[str] = None) -> List[schemas.ShowBlogWithCommentCount]:
    # Запрос для получения блогов с подсчетом только проверенных комментариев
    comment_count_query = func.coalesce(func.count(models.Comment.id), 0)  # Устанавливаем 0, если нет проверенных комментариев
    if sort_order not in [None, "asc", "desc"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid sort order. Use 'asc', 'desc', or omit it.")
    
    if sort_order == "asc":
        blogs = (
            db.query(
                models.Blog,
                comment_count_query.label("comment_count")
            )
            .outerjoin(models.Comment, (models.Blog.id == models.Comment.blog_id) & (models.Comment.is_moderated == True))  # Только проверенные комментарии
            .group_by(models.Blog.id)
            .order_by(comment_count_query.asc())
            .all()
        )
    elif sort_order == "desc":
        blogs = (
            db.query(
                models.Blog,
                comment_count_query.label("comment_count")
            )
            .outerjoin(models.Comment, (models.Blog.id == models.Comment.blog_id) & (models.Comment.is_moderated == True))
            .group_by(models.Blog.id)
            .order_by(comment_count_query.desc())
            .all()
        )
    else:
        blogs = (
            db.query(
                models.Blog,
                comment_count_query.label("comment_count")
            )
            .outerjoin(models.Comment, (models.Blog.id == models.Comment.blog_id) & (models.Comment.is_moderated == True))
            .group_by(models.Blog.id)
            .all()
        )

    # Формируем список результатов
    result = []
    for blog, comment_count in blogs:
        result.append({
            "id": blog.id,
            "title": blog.title,
            "body": blog.body,
            "creator": blog.creator,
            "comment_count": comment_count
        })

    return result

def create(request: schemas.BlogBase2,db: Session,current_user: models.User,photo_id: int = None):
    # Проверка на наличие заголовка и тела блога
    if not request.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required.")
    
    if not request.body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body is required.")
    
    if request.category_names and len(request.category_names) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A maximum of 5 categories is allowed.")

    # Если photo_id указан, проверяем существование фотографии и её принадлежность пользователю
    photo = None
    if photo_id:
        photo = db.query(models.Photo).filter(models.Photo.id == photo_id,models.Photo.user_id == current_user.id).first()
        
        if not photo:
            raise HTTPException(status_code=404, detail="Photo not found or you don't have permission. You can only attach your own photos.")

    # Если категории не указаны, создаем блог без категорий
    if not request.category_names or len(request.category_names) == 0:
        new_blog = models.Blog(
            title=request.title, 
            body=request.body, 
            user_id=current_user.id,
            categories=None,  # Указываем None, если не требуется связывать с категориями
            photo_id=photo.id if photo else None  # Привязываем фото, если оно указано
        )
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        return new_blog

    # Поиск существующих категорий по их названиям
    existing_categories = db.query(models.Category).filter(models.Category.name.in_(request.category_names)).all()
    existing_category_names = {category.name for category in existing_categories}
    
    # Определение новых категорий, которых нет в базе
    new_category_names = set(request.category_names) - existing_category_names

    # Создание новых категорий
    if new_category_names:
        new_categories = [models.Category(name=name) for name in new_category_names]
        db.add_all(new_categories)
        db.commit()

    # Получаем все категории (существующие + новые)
    all_categories = existing_categories + db.query(models.Category).filter(models.Category.name.in_(new_category_names)).all()

    # Создание нового блога с категориями и фото
    new_blog = models.Blog(
        title=request.title, 
        body=request.body, 
        user_id=current_user.id,  
        categories=all_categories if all_categories else None,
        photo_id=photo.id if photo else None  # Привязываем фото, если оно указано
    )

    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog

   
def destroy(id: int, db: Session):
    # Ищем блог по ID, без проверки user_id
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    # Проверяем, существует ли блог
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found.")

    # Удаляем блог
    db.delete(blog)
    db.commit()
    return JSONResponse(content={"detail": "Blog deleted successfully"}, status_code=status.HTTP_200_OK)


def update(id: int, request: schemas.BlogBase, db: Session, current_user: models.User):
    # Поиск блога по ID
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found.")

    # Проверка, что текущий пользователь является автором блога
    if blog.user_id != current_user.id:  # Сравниваем поле user_id с текущим пользователем
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to update this blog.")

    # Проверка на наличие заголовка и тела блога
    if not request.title or not request.body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and body are required.")

    # Обновляем заголовок и тело блога
    blog.title = request.title
    blog.body = request.body

    if request.photo_id != 0:
        # Поиск фото по ID
        photo = db.query(models.Photo).filter(models.Photo.id == request.photo_id).first()

        if not photo:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Photo with id {request.photo_id} not found.")

        # Проверяем, принадлежит ли фото текущему пользователю
        if photo.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to attach this photo.")

        # Обновляем фотографию, ассоциированную с блогом
        blog.photo = photo  # Связываем блог с новым фото
        blog.photo_id = request.photo_id
    
    # Обновляем категорию по названию, если указано category_names
    if request.category_names:
        # Если category_names - строка, преобразуем её в список
        if isinstance(request.category_names, str):
            request.category_names = [request.category_names]

        # Ищем категории по названиям
        categories = db.query(models.Category).filter(models.Category.name.in_(request.category_names)).all()

        if not categories:
            # Если категории не существуют, создаем новые
            categories = [models.Category(name=name) for name in request.category_names]
            db.add_all(categories)
            db.commit()

        # Привязываем блог к найденным или новым категориям
        blog.categories = categories  # Предположим, что у блога может быть несколько категорий
        blog.category_ids = [category.id for category in categories]

    db.commit()
    return JSONResponse(content={"detail": "Blog updated successfully"}, status_code=status.HTTP_200_OK)


def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    return blog
