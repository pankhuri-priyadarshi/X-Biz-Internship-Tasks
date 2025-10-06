from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Nice to meet you"}

@app.get("/add")
def add_numbers(a: int, b: int):
    result = a + b
    return {"a": a, "b": b, "sum": result}
