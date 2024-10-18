from pydantic import BaseModel
from typing import List
from typing import Optional

class BlogBase(BaseModel):
    title: str
    body: str
    
 
class Blog(BlogBase):
    class Config():
        orm_mode = True                    

class User(BaseModel):
    name: str
    email: str
    password: str
    

class ShowUser(BaseModel):
    name: str
    email: str  
    blogs: List[Blog] = []
    class Config():
        orm_mode = True
    
           
           
           
class ShowBlog(BaseModel):
    title: str
    body: str
    creator: ShowUser
    class Config():
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

# Обратите внимание на "ShowComment", которое используется в ShowBlog для отображения комментариев.
    