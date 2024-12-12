from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .. import schemas, database, models, token
from ..hashing import Hash
from sqlalchemy.orm import Session
router = APIRouter(tags=['Authentication'])

# Декоратор, который обозначает, что этот метод будет обрабатывать POST-запросы на путь /login.
@router.post('/login')
#  В параметре request FastAPI автоматически извлекает данные из формы, отправленной в запросе (имя пользователя и пароль), благодаря использованию зависимости OAuth2PasswordRequestForm
# Depends(database.get_db) - эта зависимость подключает к методу объект сессии базы данных 
def login(request:OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    #ищем пользователя по его email 
    user = db.query(models.User).filter(models.User.email == request.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Invalid Credentials")
    #проверка пароля
    if not Hash.verify(user.password, request.password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Incorrect password")
    #при валидных данных входа создаётся токен, куда передаём id как часть данных
    access_token = token.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
