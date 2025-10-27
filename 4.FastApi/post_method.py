from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic check
class User(BaseModel):
    name: str
    email: str
    age: int

@app.post("/register")
def register_user(user: User):
    return {
        "message": f"User {user.name} registered successfully!",
        "data": {
            "name": user.name,
            "email": user.email,
            "age": user.age
        }
    }

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI POST example"}
