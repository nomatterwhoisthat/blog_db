from fastapi import FastAPI, Request
from . import models
from .database import engine
from .routers import blog, user, authentication, comment, category
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
import os
import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from random import randint
import uuid
app = FastAPI()

# from fastapi.staticfiles import StaticFiles

# app.mount("/static", StaticFiles(directory="static"), name="static")
IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": [error['msg'] for error in exc.errors()]},
    )
# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = []
#     for error in exc.errors():
#         # Проверяем, связано ли сообщение с ошибкой формата email
#         if error['loc'][-1] == "email" and error['type'] == "string_pattern_mismatch":
#             errors.append("Email address is not valid")
#         else:
#             errors.append(error['msg'])

#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={"detail": errors},
#     )
#print("Создание таблиц в базе данных...")
models.Base.metadata.create_all(engine)
#print("Таблицы созданы успешно!")

 
# @app.post("/upload/")
# def create_upload_file(file: UploadFile = File(...)):
#     file.filename = f"{uuid.uuid4()}.jpg"
#     contents = file.file.read()  # Синхронное чтение файла
    
#     # Проверка и создание директории, если её нет
#     if not os.path.exists(IMAGEDIR):
#         os.makedirs(IMAGEDIR)
#         logging.info(f"Created directory '{IMAGEDIR}'.")

#     file_path = os.path.join(IMAGEDIR, file.filename)
#     with open(file_path, "wb") as f:
#         f.write(contents)

#     logging.info(f"File saved to '{file_path}'")
    
#     return {"filename": file.filename}

# @app.get("/show/")
# def read_random_file():
#     try:
#         # Получаем список файлов из директории
#         files = os.listdir(IMAGEDIR)
#         if not files:
#             raise HTTPException(status_code=404, detail="No files found in the image directory")

#         # Выбираем случайный файл из списка
#         random_index = randint(0, len(files) - 1)
#         file_path = os.path.join(IMAGEDIR, files[random_index])

#         # Возвращаем файл
#         return FileResponse(file_path)
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

app.include_router(authentication.router)
app.include_router(blog.router)
app.include_router(user.router)
app.include_router(comment.router)
app.include_router(category.router)
