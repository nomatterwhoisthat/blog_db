from fastapi import FastAPI #основной класс для создания веб-приложения
from . import models
from .database import engine #Объект SQLAlchemy, управляющий соединением с базой данных
from .routers import blog, user, authentication, comment, category
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi.exceptions import RequestValidationError
from fastapi import FastAPI
#Создается экземпляр приложения, который будет запускаться сервером
#Все маршруты подключаются к этому экземпляру
app = FastAPI()

#Когда входной запрос не проходит проверку, FastAPI выбрасывает RequestValidationError.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [error['msg'] for error in exc.errors()]},
    )
models.Base.metadata.create_all(engine)#создает табоицы

#добавление маршрутов
app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(comment.router)
app.include_router(category.router)
