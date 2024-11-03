from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, oauth2, models
from ..repository import comment
from typing import List
from ..rbac import check_admin, check_moderator

router = APIRouter(
    prefix="/comment",
    tags=['Comments']
)

get_db = database.get_db

@router.post('/{blog_id}', status_code=status.HTTP_201_CREATED)
def create_comment(blog_id: int, request: schemas.Comment, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return comment.create_comment(request, blog_id, current_user.id, db)



# @router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
# def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
#     return comment.delete_comment(comment_id, current_user.id, db)
@router.delete('/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(oauth2.get_current_user)
):
    # Найти комментарий по ID
    comment_to_delete = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    
    if not comment_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    # Проверяем права пользователя
    if current_user.role == "moderator":
        # Если модератор, просто удаляем комментарий
        return comment.delete_comment(comment_id, db)  # Успешное удаление

    # Если пользователь не владелец комментария, проверяем, является ли он администратором
    if comment_to_delete.user_id != current_user.id:
        check_admin(current_user)  # Проверяем, является ли текущий пользователь администратором
    
    # Удаляем комментарий
    return comment.delete_comment(comment_id, db)
    

@router.put('/{comment_id}/moderate', status_code=status.HTTP_200_OK)
def moderate_comment(comment_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    check_moderator(current_user)  # Проверка на наличие роли модератора
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found.")

    comment.is_moderated = True
    db.commit()
    return {"detail": "Comment moderated successfully."}

@router.get('/{blog_id}', status_code=status.HTTP_200_OK, response_model=List[schemas.ShowComment])
def get_comments(blog_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)  # Зависимость для получения текущего пользователя
):
    if current_user.role == "moderator" or current_user.role == "admin" :  
        return comment.get_all_comments(blog_id, db)  # Возвращаем все комментарии
    else:
        # Если не модератор, возвращаем только отмодерированные комментарии
       return comment.get_moderated_comments(blog_id, db)
         