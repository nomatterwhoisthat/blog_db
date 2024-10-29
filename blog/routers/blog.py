from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from ..repository import blog
from ..rbac import check_admin
from typing import Optional
from sqlalchemy import func
router = APIRouter(
    prefix="/blog",
    tags=['Blogs']
)

get_db = database.get_db

@router.get('/', response_model=List[schemas.ShowBlog])
def all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.get_all(db)

@router.get("/blogs/sorted_by_length", response_model=List[schemas.ShowBlogWithLength])
def get_sorted_blogs(sort_order: Optional[str] = None, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.sort_blogs_by_length(db, sort_order)


@router.get("/blogs/sorted_by_comments_number", response_model=List[schemas.ShowBlogWithCommentCount])
def sort_by_comments(sort_order: Optional[str] = None,db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.blogs_sorted_by_comments(db, sort_order)

@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowBlog)
def create(request: schemas.BlogBase, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.create(request, db, current_user)

@router.delete("/blog/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    
    b = db.query(models.Blog).filter(models.Blog.id == id).first()
    if b.user_id != current_user.id:
        # Только администратор может удалить чужие комментарии
        check_admin(current_user)
    return blog.destroy(id, current_user.id, db)    
    

@router.put('/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id: int, request: schemas.BlogBase, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.update(id, request, db)

@router.get('/{id}', status_code=200, response_model=schemas.ShowBlog)
def show(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.show(id, db)