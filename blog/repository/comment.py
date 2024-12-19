from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from .. import models, schemas
from blog.repository import notification
from typing import List
from fastapi.responses import JSONResponse

def get_all_comments(blog_id: int, db: Session) -> List[schemas.ShowComment]:
    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id).all()
    return comments

def get_moderated_comments(blog_id: int, db: Session) -> List[schemas.ShowCommentForUsers]:
    comments = db.query(models.Comment).filter(models.Comment.blog_id == blog_id, models.Comment.is_moderated == True).all()
    return comments

def create_comment(request: schemas.Comment, blog_id: int, user_id: int, parent_comment: str, db: Session):
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
    if not blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    
    # Проверяем, указан ли текст комментария
    if not request.content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Comment content is required.")
    
    new_comment = models.Comment(
        content=request.content,
        blog_id=blog_id,
        user_id=user_id,
        parent_id=parent_comment.id if parent_comment else None  # Связь с родительским комментарием
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    if parent_comment:
        content = f" The user '{new_comment.author.name}' left a comment: {new_comment.content[:50]}... to your previous comment on the blog '{parent_comment.blog.title}'"
        notification.create_notification(parent_comment.user_id, content, db)
    return new_comment

# def delete_comment(comment_id: int, db: Session):
#     comment_to_delete = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
#     if comment_to_delete:
#         db.delete(comment_to_delete)
#         db.commit()
#     else:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")
#     return JSONResponse(content={"detail": "Comment deleted successfully"}, status_code=status.HTTP_200_OK)

def delete_comment(comment_id: int, db: Session, current_user: models.User):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Уведомление о модерации
    if current_user.role in ["admin", "moderator"]:
        content = f"Your comment on the blog '{comment.blog.title}' has been removed due to inappropriate content or spam."
        notification.create_notification(comment.user_id, content, db)

    db.delete(comment)
    db.commit()
    return JSONResponse(content={"detail": "Comment deleted successfully"}, status_code=status.HTTP_200_OK)