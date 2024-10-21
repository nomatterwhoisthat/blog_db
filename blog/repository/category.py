from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

def get_all_categories(db: Session):
    return db.query(models.Category).all()

def create_category(request: schemas.Category, db: Session):
    new_category = models.Category(name=request.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def get_blogs_by_category_name(category_name: str, db: Session):
    # Получаем категорию по названию
    category = db.query(models.Category).filter(models.Category.name == category_name).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # Получаем блоги, связанные с этой категорией
    blogs = category.blogs
    return blogs
