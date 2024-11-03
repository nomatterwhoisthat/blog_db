from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from fastapi.responses import JSONResponse
from typing import List
# def get_all_comments(blog_id: int, db: Session):
#     comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
#     return comments

# def create_comment(request: schemas.Comment, blog_id: int, user_id: int, db: Session):
#     # Проверка на содержание комментария
#     if not request.content:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content is required.")

#     new_comment = models.Comment(content=request.content, blog_id=blog_id, user_id=user_id)
#     db.add(new_comment)
#     db.commit()
#     db.refresh(new_comment)
#     return new_comment

# repository/comment.py
def get_all_comments(blog_id: int, db: Session) -> List[schemas.ShowComment]:
    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
    return comments

def get_moderated_comments(blog_id: int, db: Session) -> List[schemas.ShowCommentForUsers]:
    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id, models.Comment.is_moderated == True).all()
    return comments

def create_comment(request: schemas.Comment, blog_id: int, user_id: int, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    
    # Проверяем, указан ли текст комментария
  
    if not request.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content is required.")

    new_comment = models.Comment(content=request.content, blog_id=blog_id, user_id=user_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

# def delete_comment(comment_id: int, user_id: int, db: Session):
#     comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.user_id == user_id).first()

#     if not comment:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not authorized.")

#     db.delete(comment)
#     db.commit()
#     return JSONResponse(content={"detail": "Comment deleted successfully"}, status_code=status.HTTP_200_OK)

def delete_comment(comment_id: int, db: Session):
    comment_to_delete = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if comment_to_delete:
        db.delete(comment_to_delete)
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
    return JSONResponse(content={"detail": "Comment deleted successfully"}, status_code=status.HTTP_200_OK)
