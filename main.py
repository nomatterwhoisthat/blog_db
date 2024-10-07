from fastapi import FastAPI


app = FastAPI() #the instance

@app.get('/')

def index():
    return 'hi'