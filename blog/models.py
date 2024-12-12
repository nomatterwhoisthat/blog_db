from sqlalchemy import Column, Integer, String, ForeignKey, Table, Boolean
from .database import Base
from sqlalchemy.orm import relationship

# Таблица для связи многие ко многим между блогами и категориями
blog_category = Table('blog_category', Base.metadata,
    Column('blog_id', Integer, ForeignKey('blogs.id')),
    Column('category_id', Integer, ForeignKey('categories.id'))
)

class Photo(Base):
    __tablename__ = 'photos'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
      
    user = relationship("User", back_populates="photos")
    blog = relationship("Blog", back_populates="photo", uselist=False)

class Blog(Base):
    __tablename__ = 'blogs'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  
    body = Column(String, nullable=False)  
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 
    photo_id = Column(Integer, ForeignKey('photos.id'), nullable=True)

    creator = relationship("User", back_populates="blogs")
    comments = relationship("Comment", back_populates="blog", cascade="all, delete")
    categories = relationship("Category", secondary='blog_category', back_populates="blogs")
    photo = relationship("Photo", back_populates="blog")



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    role = Column(String, default="guest")  # Роль по умолчанию - гость

    blogs = relationship("Blog", back_populates="creator")
    comments = relationship("Comment", back_populates="author", cascade="all, delete")
    photos = relationship("Photo", back_populates="user", cascade="all, delete")
    
class Comment(Base):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String)
    blog_id = Column(Integer, ForeignKey('blogs.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    is_moderated = Column(Boolean, default=False)
    parent_id = Column(Integer, ForeignKey('comments.id'), nullable=True)  # Поле для родительского комментария

    blog = relationship("Blog", back_populates="comments")
    author = relationship("User", back_populates="comments")
    parent = relationship("Comment", remote_side=[id], backref="replies")  # Связь с родительским комментарием


class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    blogs = relationship("Blog", secondary=blog_category, back_populates="categories")