from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class NotificationBase(BaseModel):
    content: str = Field(..., max_length=500, description="Текст уведомления")

class ShowNotification(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class BlogBase(BaseModel):
    title: str = Field(..., max_length=255, description="Заголовок блога (макс. 255 символов)")
    body: str = Field(..., min_length=1, max_length=20000, description="Тело блога (мин. 1 символ)")
    category_names: Optional[List[str]] = Field([], max_length=5, description="Список имен категорий (можно оставить пустым)")
    photo_id: Optional[int] = Field(None, description="Идентификатор фотографии (необязательное поле)")

class BlogBase2(BaseModel):
    title: str = Field(..., max_length=255, description="Заголовок блога (макс. 255 символов)")
    body: str = Field(..., min_length=1, max_length=20000, description="Тело блога (мин. 1 символ)")
    category_names: Optional[List[str]] = Field(...,max_length=5, description="Список имен категорий (можно оставить пустым)")
    

class CategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="Название категории (макс. 100 символов)")

class Category(CategoryBase):
    class Config:
        orm_mode = True

class ShowCategory(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True

class Blog(BlogBase):
    class Config:
        orm_mode = True                    


class User(BaseModel):
    name: str = Field(..., max_length=100, description="Имя пользователя (макс. 100 символов)")
    email: str = Field(..., pattern=r'^\S+@\S+\.\S+$', description="Электронная почта пользователя (должна соответствовать формату email)")
    password: str = Field(..., min_length=6, description="Пароль (мин. 6 символов)")
    role: Optional[str] = "guest"  # По умолчанию роль - гость

    
class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    role: str  
    class Config:
        orm_mode = True
        from_attributes = True
        
class PhotoBase(BaseModel):
    filename: str

class ShowPhoto(PhotoBase):
    id: int
    
class ShowBlog(BaseModel):
    id: int
    title: str
    body: str
    creator: ShowUser
    categories: List[ShowCategory]
    photo: Optional[ShowPhoto] = None 
    class Config:
        orm_mode = True

class Login(BaseModel):
    name: str
    password: str        

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: int

class CommentBase(BaseModel):
    content: str = Field(..., max_length=256, description="Содержимое комментария (минимум 1 символ)")
    parent_id: Optional[int] = None  # ID родительского комментария (если есть)


class Comment(CommentBase):
    class Config:
        orm_mode = True

class ShowComment(BaseModel):
    id: int
    blog_id: int
    content: str
    author: ShowUser
    is_moderated: Optional[bool] = None
    parent_id: Optional[int] = None  # ID родительского комментария
    replies: List["ShowComment"] = []  # Ответы на комментарий

    class Config:
        orm_mode = True


class ShowCommentForUsers(BaseModel):
    id: int
    content: str
    author: ShowUser
    
    class Config:
        orm_mode = True


class ShowBlogWithCommentCount(BaseModel):
    id: int
    title: str
    body: str
    creator: ShowUser  
    comment_count: int  
    
    class Config:
        from_attributes = True 


class ShowBlogWithLength(BaseModel):
    id: int
    title: str
    body: str
    creator: ShowUser  
    length: int 
    
