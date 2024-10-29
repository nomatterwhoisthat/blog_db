from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import func
from typing import Optional, List
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


def create(request: schemas.BlogBase, db: Session, current_user: models.User):
    # Проверка на наличие заголовка и тела блога
    if not request.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required.")
    
    if not request.body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body is required.")
    
    if request.category_names and len(request.category_names) > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A maximum of 5 categories is allowed.")

    # Если категории не указаны, создаем блог без категорий
    if not request.category_names or len(request.category_names) == 0:
        new_blog = models.Blog(
            title=request.title, 
            body=request.body, 
            user_id=current_user.id,
            categories=None  # Указываем None, если не требуется связывать с категориями
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
    if new_category_names:  # Проверяем, есть ли новые категории для создания
        new_categories = [models.Category(name=name) for name in new_category_names]
        db.add_all(new_categories)
        db.commit()

    # Получаем все категории (существующие + новые)
    all_categories = existing_categories + db.query(models.Category).filter(models.Category.name.in_(new_category_names)).all()

    # Создание нового блога с категориями
    new_blog = models.Blog(
        title=request.title, 
        body=request.body, 
        user_id=current_user.id,  
        categories=all_categories if all_categories else None  # Устанавливаем None, если категорий нет
    )

    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)

    return new_blog

def destroy(id: int, user_id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id, models.Blog.user_id == user_id ).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found.")

    db.delete(blog)
    db.commit()
    return JSONResponse(content={"detail": "Blog deleted successfully"}, status_code=status.HTTP_200_OK)




def update(id: int, request: schemas.BlogBase, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found.")

    # Проверка на наличие заголовка и тела блога
    if not request.title or not request.body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and body are required.")

    blog.title = request.title
    blog.body = request.body
    db.commit()
    return JSONResponse(content={"detail": "Blog updated successfully"}, status_code=status.HTTP_200_OK)



def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {id} is not available")
    return blog