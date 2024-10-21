from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas

def get_all_comments(blog_id: int, db: Session):
    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
    return comments

def create_comment(request: schemas.Comment, blog_id: int, user_id: int, db: Session):
    new_comment = models.Comment(content=request.content, blog_id=blog_id, user_id=user_id)
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

def delete_comment(comment_id: int, user_id: int, db: Session):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id, models.Comment.user_id == user_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found or not authorized")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted successfully"}
