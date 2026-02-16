from email import message
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List
from starlette.exceptions import HTTPException as StarletteHttpException
from schemas import PostCreate, PostResponse

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

posts: List[dict] = [
    {
        "id": 1,
        "author": "Zeeshan Latif",
        "title": "FastAPI",
        "content": "FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Smith",
        "title": "FastAPI 2",
        "content": "FastAPI 2 is a modern, fast (high-performance), web framework for building APIs with Python 3.7+ based on standard Python type hints.",
        "date_posted": "April 30, 2025",
    }
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def home(request: Request):
    return templates.TemplateResponse(request, "home.html", {"posts" : posts, "title": "Home"})


@app.get("/posts/{post_id}", include_in_schema=False)
def post_page(request: Request, post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            title = post["title"][:50]
            return templates.TemplateResponse(request, "post.html", {"post" : post, "title": title}) 
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.get("/api/posts", response_model=List[PostResponse])
def get_posts():
    return posts

@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int):
    for post in posts:
        if post.get("id") == post_id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "author": post.author,
        "title" : post.title,
        "content": post.content,
        "date_posted": "Feb 16, 2026"
    }

    posts.append(new_post)
    return new_post


@app.exception_handler(StarletteHttpException)
def general_http_exception_handler(request: Request, exception: StarletteHttpException):
    message = (
        exception.detail if exception.detail else "An error occurred. Please check your request and try again."
    )

    if request.url.path.startswith("/api"):
        return JSONResponse(status_code=exception.status_code, content={"detail" : message})

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": exception.status_code,
            "title": exception.status_code,
            "message": message,
        },
        status_code=exception.status_code,
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exception: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={"detail": exception.errors()},
        )

    return templates.TemplateResponse(
        request,
        "error.html",
        {
            "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "title": status.HTTP_422_UNPROCESSABLE_CONTENT,
            "message": "Invalid request. Please check your input and try again.",
        },
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    )