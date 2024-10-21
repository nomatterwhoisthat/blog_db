from sqlalchemy.orm import Session
from .. import models, schemas
from fastapi import HTTPException, status

def get_all(db: Session):
    blogs = db.query(models.Blog).all()
    return blogs

# repository/blog.py

def create(request: schemas.BlogBase, db: Session, current_user: models.User):
    # Поиск категорий по их названиям
    existing_categories = db.query(models.Category).filter(models.Category.name.in_(request.category_names)).all()
    
    existing_category_names = {category.name for category in existing_categories}
    new_category_names = set(request.category_names) - existing_category_names
    
    new_categories = [models.Category(name=name) for name in new_category_names]
    db.add_all(new_categories)
    db.commit()
    
    all_categories = existing_categories + new_categories
    
    # Создание нового блога с привязкой к текущему пользователю
    new_blog = models.Blog(
        title=request.title, 
        body=request.body, 
        user_id=current_user.id,  # Привязываем блог к текущему пользователю
        categories=all_categories
    )
    
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    
    return new_blog  # Возвращаем блог с полем creator

def destroy(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {id} is not available")
    
    db.delete(blog)
    db.commit()
    return 'done'

def update(id: int, request: schemas.BlogBase, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {id} is not available")

    # Преобразуем объект Pydantic в словарь
    blog.update(request.dict())
    db.commit()
    
    return 'Blog updated successfully'

def show(id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Blog with the id {id} is not available")
    return blog