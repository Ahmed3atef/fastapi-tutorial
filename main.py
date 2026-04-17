from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


posts: list[dict] = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def root(request: Request) -> HTMLResponse:
    context_dict = {
        "title": "Home",
        "posts": posts
    }
    return templates.TemplateResponse(request, "home.html", context=context_dict)

@app.get("/api/posts")
def get_posts() -> list[dict]:
    return posts

@app.get("/api/posts/{id}")
def get_one_post(id: int) -> dict:
    for post in posts:
        if post["id"] == id:
            return post
    return {"error": "Post not found"}