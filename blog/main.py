from fastapi import FastAPI
from . import models
from .database import engine
from .routers import blog, user, authentication, comment, category
from .rbac import RBACMiddleware
app = FastAPI()

# Добавьте вывод для проверки
#print("Создание таблиц в базе данных...")
models.Base.metadata.create_all(engine)
#print("Таблицы созданы успешно!")

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(comment.router)
app.include_router(category.router)
