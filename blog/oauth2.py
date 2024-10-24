from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .token import SECRET_KEY, ALGORITHM, JWTError, jwt, verify_token
from . import database, models
from .schemas import TokenData
get_db=database.get_db
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(data: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(data, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    
    if user is None:
        raise credentials_exception
    
    return user
    

# def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
    
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id: int = int(payload.get("id"))  # Получаем id из токена
        
#         if user_id is None:
#             raise credentials_exception
        
#         token_data = TokenData(id=user_id)  # Передаем id
#     except JWTError:
#         raise credentials_exception

#     user = db.query(models.User).filter(models.User.id == token_data.id).first()
    
#     if user is None:
#         raise credentials_exception
    
#     return user
