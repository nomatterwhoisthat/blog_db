from fastapi import APIRouter, Depends, status,  HTTPException
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from ..repository import user
from ..rbac import check_admin
from typing import List

router = APIRouter(
    prefix="/user",
    tags=['users']
)

get_db = database.get_db

@router.post('/', response_model=schemas.ShowUser)
def create_user(request: schemas.User,  db: Session = Depends(get_db)):
   return user.create(request, db)

@router.get('/', response_model=List[schemas.ShowUser])  # Добавьте новый маршрут для получения всех пользователей
def get_users(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    check_admin(current_user)  # Проверка на наличие роли администратора
    return db.query(models.User).all()  # Возвращаем всех пользователей

@router.get('/{id}', response_model=schemas.ShowUser)
def get_user(id: int,  db: Session = Depends(get_db)):
    return user.show(id, db)


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # Проверка, если текущий пользователь не найден
    u = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Если пользователь не найден
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    
    # Проверка прав доступа: текущий пользователь должен быть администратором или удалять только себя
    if u.id != current_user.id:
        check_admin(current_user)
    
    return user.destroy_user(user_id, current_user.id, db)