from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, database, models, oauth2
from ..repository import category 

router = APIRouter(
    prefix="/category",
    tags=['Categories']
)

get_db = database.get_db

@router.get('/', response_model=List[schemas.ShowCategory])
def get_categories(db: Session = Depends(get_db),  current_user: schemas.User = Depends(oauth2.get_current_user)):
    return category.get_all_categories(db)

# @router.get('/{category_name}/blogs', response_model=List[schemas.ShowBlog])
# def get_blogs_by_category(category_name: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
#     return category.get_blogs_by_category_name(category_name, db)

@router.get('/blogs', response_model=List[schemas.ShowBlog])
def get_blogs_by_categories(
    category_names: List[str] = Query(..., description="List of category names"),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    """
    Получение блогов, связанных с указанными категориями.

    - **category_names**: Список названий категорий.
    """
    return category.get_blogs_by_category_names(category_names, db)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowCategory)
def create_category(request: schemas.CategoryBase, db: Session = Depends(get_db),  current_user: schemas.User = Depends(oauth2.get_current_user)):
    return category.create_category(request, db)