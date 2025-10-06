from fastapi import FastAPI, Depends, Request
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
import aioredis

app = FastAPI()

# Connect Redis on startup
@app.on_event("startup")
async def startup():
    redis = await aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)

# Create a rate-limited route
@app.get("/hello", dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def hello():
    return {"message": "Hello, User! You can only call this 5 times per minute"}

@app.get("/quotes",dependencies=[Depends(RateLimiter(times=2, seconds=10))])
async def quotes():
    return {"message":"Nothing is impossible for you dude!"}

@app.exception_handler(StarletteHTTPException)
async def handle_429_error(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTP_429_TOO_MANY_REQUESTS:
        return JSONResponse(
            status_code=HTTP_429_TOO_MANY_REQUESTS,
            #headers={"Retry-After": "60"},   ---it overwrite all fn retry-limt
            content={"error": "Too Many Requests", "message": "Please wait before trying again"}
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

@app.get("/")
async def home():
    return {"message": "Welcome to FastAPI Rate Limiter Demo"}
