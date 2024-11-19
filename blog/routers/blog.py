from typing import List
from fastapi import APIRouter, Depends, status, UploadFile, File,HTTPException
from .. import schemas, database, models, oauth2
from sqlalchemy.orm import Session
from ..repository import blog
from ..rbac import check_admin
from typing import Optional
from fastapi.responses import JSONResponse
from fastapi.responses import FileResponse
router = APIRouter(
    prefix="/blog",
    tags=['Blogs']
)

get_db = database.get_db

import os
import uuid
import logging

IMAGEDIR = os.path.join(os.path.dirname(__file__), "images")

@router.post("/upload-photo/", response_model=schemas.ShowPhoto)
def upload_photo(
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: schemas.User = Depends(oauth2.get_current_user)
):
    try:
        allowed_extensions = ["jpg", "jpeg", "png"]
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Only .png and .jpg files are allowed.")

        # Генерация нового имени файла
        file.filename = f"{uuid.uuid4()}.{file_extension}"
        contents = file.file.read()  # Синхронное чтение файла
        
        # Проверка и создание директории, если её нет
        if not os.path.exists(IMAGEDIR):
            os.makedirs(IMAGEDIR)
            logging.info(f"Created directory '{IMAGEDIR}'.")

        file_path = os.path.join(IMAGEDIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(contents)

        logging.info(f"File saved to '{file_path}'")
        
        # return {"filename": file.filename}
        # Создаём запись о фото в базе данных
        
        photo = models.Photo(filename=file.filename, user_id=current_user.id)
        db.add(photo)
        db.commit()
        db.refresh(photo)

        return photo

    except Exception as e:
        logging.error(f"Failed to upload photo: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while uploading the photo.")

@router.get("/photos/", response_model=List[schemas.ShowPhoto])
def get_user_photos( db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    # Получаем все фото текущего пользователя из базы данных
    photos = db.query(models.Photo).filter(models.Photo.user_id == current_user.id).all()
    
    if not photos:
        raise HTTPException(status_code=404, detail="No photos found for the current user.")
    
    return photos

@router.get("/gallery/{photo_id}")
def get_photo_by_id(photo_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    # Ищем фотографию по ID
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    
    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    # Проверяем, является ли текущий пользователь владельцем фотографии
    if photo.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this photo")

    # Формируем путь к изображению
    image_path = os.path.join(IMAGEDIR, photo.filename)

    # Проверяем, существует ли файл
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image file not found")

    # Возвращаем изображение
    return FileResponse(image_path)


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.ShowBlog)
def create(request: schemas.BlogBase2, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user), photo_id: int = None):  # Добавляем photo_id как необязательный параметр):
    return blog.create(request, db, current_user, photo_id)

@router.post("/{blog_id}/attach-photo/{photo_id}")
def attach_photo_to_blog(blog_id: int, photo_id: int, db: Session = Depends(database.get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    # Проверка принадлежности блога
    blog = db.query(models.Blog).filter(models.Blog.id == blog_id, models.Blog.user_id == current_user.id).first()
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found or you don't have permission to attach a photo.")
    
    if blog.photo_id is not None:
        raise HTTPException(status_code=400, detail="A photo is already attached to this blog. Cannot attach another photo.")

    # Проверка принадлежности фотографии
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id, models.Photo.user_id == current_user.id).first()
    if not photo:
        raise HTTPException(status_code=403, detail="You can only attach your own photos.")

    # Привязываем фотографию к блогу
    blog.photo_id = photo.id
    db.commit()
    db.refresh(blog)

    return {"detail": "Photo successfully attached to blog"}

@router.get("/blog/{blog_id}/image/")
def get_blog_image(blog_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    try:
        # Ищем блог по ID
        blog = db.query(models.Blog).filter(models.Blog.id == blog_id).first()
        
        if not blog:
            raise HTTPException(status_code=404, detail="Blog not found")

        # Путь к изображению для данного блога
        image_path = os.path.join(IMAGEDIR,  blog.photo.filename)  # Предполагаем, что image_path хранит имя файла
        print(image_path)

        # Проверяем, существует ли файл
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")

        # Возвращаем файл
        return FileResponse(image_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get('/', response_model=List[schemas.ShowBlog])
def all(db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.get_all(db)


@router.get('/{id}', status_code=200, response_model=schemas.ShowBlog)
def show(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.show(id, db)


@router.get("/blogs/sorted_by_length", response_model=List[schemas.ShowBlogWithLength])
def get_sorted_blogs(sort_order: Optional[str] = None, db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    return blog.sort_blogs_by_length(db, sort_order)


@router.get("/blogs/sorted_by_comments_number", response_model=List[schemas.ShowBlogWithCommentCount])
def sort_by_comments(sort_order: Optional[str] = None,db: Session = Depends(get_db),current_user: schemas.User = Depends(oauth2.get_current_user)):
    if current_user.role == "moderator" or current_user.role == "admin" :  
        return blog.blogs_sorted_by_comments(db, sort_order)
    else:
        return  blog.blogs_sorted_by_moderated_comments(db, sort_order)
  
@router.put("/blogs/{id}")
def update_blog(id: int, request: schemas.BlogBase, db: Session = Depends(database.get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    return blog.update(id, request, db, current_user)    

@router.delete("/blog/{id}", status_code=status.HTTP_204_NO_CONTENT)
def destroy(id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(oauth2.get_current_user)):
    
    # Ищем блог по ID
    b = db.query(models.Blog).filter(models.Blog.id == id).first()
    
    # Проверяем, существует ли блог
    if not b:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog not found.")
    
    # Проверяем, является ли пользователь владельцем блога или администратором
    if b.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this blog.")
    
    # Удаляем блог, передавая только ID блога
    return blog.destroy(id, db)
    


