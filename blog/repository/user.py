from .. import models, schemas
from sqlalchemy.orm import Session
from ..hashing import Hash
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse

def create(request: schemas.User, db: Session):
     # Проверка на уникальность имени пользователя
    existing_user = db.query(models.User).filter(models.User.name == request.name).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The name is taken. Choose the another one."
        )
    
    existing_email = db.query(models.User).filter(models.User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )    

    # Проверка на сложность пароля (пример)
    if len(request.password) < 6 or not any(char.isdigit() for char in request.password) or not any(char.isupper() for char in request.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long and contain at least one digit and one uppercase letter."
        )
    # Создание нового пользователя
    new_user = models.User(
        name=request.name,
        email=request.email,
        password=Hash.bcrypt(request.password),
        role=request.role or "guest"  # Роль по умолчанию - гость
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def show(id: int, db: Session):
    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with the id {id} is not available")
    return user


def destroy_user(user_id: int, cur_user_id: int, db: Session):
    u = db.query(models.User).filter(models.User.id == user_id).first()
    
    # Если пользователь не найден
    if not u:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    db.delete(u)
    db.commit()
    return JSONResponse(content={"detail": "Blog deleted successfully."}, status_code=status.HTTP_200_OK)

