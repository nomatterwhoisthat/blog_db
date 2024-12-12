from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .token import verify_token
from . import database, models

get_db=database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")#передача токена доступа, tokenUrl - параметр, где пользователь получит токен

#Эта функция используется как зависимость для проверки токена и извлечения данных текущего пользователя
def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):#Извлекает токен из заголовка, устанавливает подключение к бд
    #Если токен недействителен или пользователь не найден, будет вызвано исключение
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(data, credentials_exception)
    #verify_token (из модуля token) декодирует токен и проверяет его валидность.
    #Если токен недействителен (например, истёк), будет выброшено исключение credentials_exception.
    #При успешной проверке возвращаются данные токена (например, ID пользователя)
    
    #запрос к таблице User для поиска пользователя с указанным id, который был извлечён из токена.
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    
    if user is None:
        raise credentials_exception
    
    return user
    
