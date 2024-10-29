from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime
from sqlalchemy.sql import func
from .database import Base
from sqlalchemy.orm import relationship

# Таблица для связи многие ко многим между блогами и категориями
blog_category = Table('blog_category', Base.metadata,
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)


class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  
    body = Column(String, nullable=False)  
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 

    creator = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete")
    categories = relationship("Category", secondary='blog_category', back_populates="blogs")



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String, default="guest")  # Роль по умолчанию - гость

    blogs = relationship("Blog", back_populates="creator")
    comments = relationship("Comment", back_populates="author", cascade="all, delete")
    
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    blog_id = Column(Integer, ForeignKey('blogs.id'))
    user_id = Column(Integer, ForeignKey('users.id'))

    blog = relationship("Blog", back_populates="comments")
    author = relationship("User", back_populates="comments")

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    blogs = relationship("Blog", secondary=blog_category, back_populates="categories")