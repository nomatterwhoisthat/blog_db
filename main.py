from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel
app = FastAPI() #the instance

@app.get('/blog')
def index(limit = 10, published: bool = True, sort: Optional[str] = None):
    if published:
        return {'data' : f' {limit} published blogs from the db'}
    else:
        return {'data' : f'{limit} all blogs from the db'}

@app.get('/about')
def about():
    return{'data': 'about page'}

@app.get('/blog/unpublished')
def unpublished():
    return{'data': 'all unpublished blogs'}

@app.get('/blog/{id}')
def show(id: int):
    return{'data': id}

@app.get('/blog/{id}/comments')
def comments(id, limit=10):
    return{'data': {'1', '2'}}

class Blog(BaseModel):
    title: str
    body: str
    published: Optional[bool]
   # pass

@app.post('/blog')
def create_blog(request: Blog):
    return {'data': f"Blog is created with title as {request.title}"}