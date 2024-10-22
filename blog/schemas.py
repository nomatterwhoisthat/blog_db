from pydantic import BaseModel, Field
from typing import List, Optional


class BlogBase(BaseModel):
    title: str = Field(..., max_length=255, description="Заголовок блога (макс. 255 символов)")
    body: str = Field(..., min_length=1, max_length=1000000, description="Тело блога (мин. 1 символ)")
    category_names: Optional[List[str]] = Field(None, description="Список имен категорий (можно оставить пустым)")


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
 
class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True

class ShowBlog(BaseModel):
    id: int
    title: str
    body: str
    creator: ShowUser
    categories: List[ShowCategory]
    class Config:
        orm_mode = True

class Login(BaseModel):
    username: str
    password: str        

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None 

class CommentBase(BaseModel):
    content: str = Field(..., max_length=256, description="Содержимое комментария (минимум 1 символ)")

class Comment(CommentBase):
    class Config:
        orm_mode = True

class ShowComment(BaseModel):
    id: int
    content: str
    author: ShowUser
    class Config:
        orm_mode = True
