from pydantic import BaseModel
from typing import List
from typing import Optional

# schemas.py

class BlogBase(BaseModel):
    title: str
    body: str
    category_names: List[str]  # Здесь список имен категорий

class CategoryBase(BaseModel):
    name: str

class Category(CategoryBase):
    class Config:
        orm_mode = True

class ShowCategory(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True


 
class Blog(BlogBase):
    class Config():
        orm_mode = True                    

class User(BaseModel):
    name: str
    email: str
    password: str
 
class ShowUser(BaseModel):
    id: int
    name: str
    email: str
    class Config():
        orm_mode = True


class ShowBlog(BaseModel):
    id: int
    title: str
    body: str
    creator: ShowUser
    categories: List[ShowCategory]  # Добавьте категории в вывод
    class Config:
        orm_mode = True

# class ShowBlog(BaseModel):
#     title: str
#     body: str
#     creator: ShowUser
#     class Config():
#         orm_mode = True           
        
# schemas.py

# class ShowBlog(BaseModel):
#     title: str
#     body: str
#     creator: ShowUser
#     categories: List[ShowCategory]  # Отображение категорий блога
#     class Config():
#         orm_mode = True
   
       
class Login(BaseModel):
    username: str
    password: str        
    
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[int] = None 
    

class CommentBase(BaseModel):
    content: str

class Comment(CommentBase):
    class Config:
        orm_mode = True

class ShowComment(BaseModel):
    id: int
    content: str
    author: ShowUser
    class Config:
        orm_mode = True