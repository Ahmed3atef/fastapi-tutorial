from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI()

posts = [
    {"title": "Post 1", "content": "Content 1"},
    {"title": "Post 2", "content": "Content 2"},
    {"title": "Post 3", "content": "Content 3"},
]

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root() -> dict[str, str]:
    return "<h1>Hello World</h1>"

@app.get("/api/posts")
def get_posts() -> list[dict[str, str]]:
    return posts

@app.get("/api/posts/{id}")
def get_one_post(id: int) -> dict[str, str]:
    return posts[id-1]