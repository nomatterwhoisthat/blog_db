from fastapi import FastAPI, Request
from . import models
from .database import engine
from .routers import blog, user, authentication, comment, category
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError

app = FastAPI()
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [error['msg'] for error in exc.errors()]},
    )

#print("Создание таблиц в базе данных...")
models.Base.metadata.create_all(engine)
#print("Таблицы созданы успешно!")


app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(comment.router)
app.include_router(category.router)
