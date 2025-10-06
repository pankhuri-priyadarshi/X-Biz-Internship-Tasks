from fastapi import FastAPI

app=FastAPI()
def add(a,b):
    return a+b

@app.get('/')
def greet():
    a=add(7,8)
    return f"Hello {a}"
    #return {"message":"Hello from FastAPI"}


