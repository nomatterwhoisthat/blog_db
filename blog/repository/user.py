from .. import models, schemas
from sqlalchemy.orm import Session
from ..hashing import Hash
from fastapi import HTTPException, status

def create(request: schemas.User, db: Session):
    # Проверка на уникальность имени пользователя
    existing_user = db.query(models.User).filter(models.User.name == request.name).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The name is taken.")

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