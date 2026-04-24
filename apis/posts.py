from settings import app
from fastapi import status, HTTPException
from db.json import posts



@app.get("/api/posts")
def get_posts() -> list[dict]:
    return posts

@app.get("/api/posts/{id}")
def get_post(id: int) -> dict:
    for post in posts:
        if post.get("id") == id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found!")
