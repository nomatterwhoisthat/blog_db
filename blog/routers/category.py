from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, models
from ..repository import category 

router = APIRouter(
    prefix="/category",
    tags=['Categories']
)

get_db = database.get_db

@router.get('/', response_model=List[schemas.ShowCategory])
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Category).all()
    return categories

@router.get('/{category_name}/blogs', response_model=List[schemas.ShowBlog])
def get_blogs_by_category(category_name: str, db: Session = Depends(get_db)):
    return category.get_blogs_by_category_name(category_name, db)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowCategory)
def create_category(request: schemas.CategoryBase, db: Session = Depends(get_db)):
    return category.create_category(request, db)