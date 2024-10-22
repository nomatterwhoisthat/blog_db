from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, oauth2
from ..repository import comment
from typing import List


router = APIRouter(
    prefix="/comment",
    tags=['Comments']
)

get_db = database.get_db

@router.post('/{blog_id}', status_code=status.HTTP_201_CREATED)
def create_comment(blog_id: int, request: schemas.Comment, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return comment.create_comment(request, blog_id, current_user.id, db)

@router.get('/{blog_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.ShowComment])
def get_comments(blog_id: int, db: Session = Depends(get_db)):
    return comment.get_all_comments(blog_id, db)

@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return comment.delete_comment(comment_id, current_user.id, db)