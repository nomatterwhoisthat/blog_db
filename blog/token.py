from datetime import datetime, timedelta
from jose import JWTError, jwt
from . import schemas

SECRET_KEY = "88316380497e20a1655ce0c9d583197ad844decc1516cb1fcfdae1b4b3bbfd68"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token:str,credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("sub")
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=int(id))
        return token_data
    except JWTError:
        raise credentials_exception