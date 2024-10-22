from sqlalchemy.orm import Session
from .. import schemas
from .. import models
from fastapi import HTTPException, status

def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs

# from sqlalchemy.orm import Session
# from fastapi import HTTPException, status
# from typing import List
# from . import models, schemas

def create(request: schemas.BlogBase, db: Session, current_user: models.User):
    # Проверка на наличие заголовка и тела блога
    if not request.title:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required.")
    
    if not request.body:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Body is required.")

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

def destroy(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()

    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with id {id} not found.")

    db.delete(blog)
    db.commit()
    return 'Blog deleted successfully'



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

    return 'Blog updated successfully'


def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {id} is not available")
    return blog