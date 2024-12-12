from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import schemas

SECRET_KEY = "88316380497e20a1655ce0c9d583197ad844decc1516cb1fcfdae1b4b3bbfd68"#Секретный ключ, который используется для подписания токенов.
ALGORITHM = "HS256"#Алгоритм шифрования токена
ACCESS_TOKEN_EXPIRE_MINUTES = 30#Время жизни токена


#Эта функция создаёт JWT-токен на основе входных данных 
def create_access_token(data: dict):
    to_encode = data.copy()# Создаётся копия переданных данных (data), чтобы сохранить исходные данные неизменными
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)#Данные шифруются с использованием библиотеки jose
    return encoded_jwt

#Эта функция проверяет и декодирует токен
def verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])#Токен расшифровывается
        id: str = payload.get("sub")#Проверяется наличие ключа "sub" в данных токена
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=int(id))#данные токена преобразуются в объект
        return token_data
    except JWTError:
        raise credentials_exception