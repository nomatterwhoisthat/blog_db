from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from typing import List
def get_all_categories(db: Session):
    return db.query(models.Category).all()

def create_category(request: schemas.Category, db: Session):
    if not request.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name is required.")

    # Проверка на уникальность имени категории
    if db.query(models.Category).filter(models.Category.name == request.name).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists.")

    new_category = models.Category(name=request.name)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

def get_blogs_by_category_names(category_names: List[str], db: Session):
    # Проверка: если категорий больше 5, выводим ошибку
    if len(category_names) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can only search for a maximum of 5 categories."
        )

    # Получаем категории, соответствующие названиям
    categories = db.query(models.Category).filter(models.Category.name.in_(category_names)).all()

    # Проверка: если хотя бы одной категории нет в базе данных
    if len(categories) != len(category_names):
        missing_categories = list(set(category_names) - {category.name for category in categories})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categories not found: {', '.join(missing_categories)}"
        )

    # Получаем идентификаторы категорий
    category_ids = {category.id for category in categories}

    # Фильтруем блоги, которые связаны с хотя бы одной из указанных категорий
    blogs = db.query(models.Blog).filter(
        models.Blog.categories.any(models.Category.id.in_(category_ids))
    ).all()

    # Отфильтровываем блоги, которые включают все указанные категории
    filtered_blogs = [
        blog for blog in blogs
        if category_ids.issubset({category.id for category in blog.categories})
    ]

    # Если блоги с нужным набором категорий не найдены, выводим ошибку
    if not filtered_blogs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No blogs found with the specified set of categories."
        )

    return filtered_blogs