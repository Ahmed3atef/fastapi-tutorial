from core import app
from fastapi import status, HTTPException
from db.json import posts
from schemas import PostResponseSerializer, PostCreateSerializer



@app.get("/api/posts", response_model=list[PostResponseSerializer])
def get_posts() -> list[dict]:
    return posts

@app.get("/api/posts/{id}", response_model=PostResponseSerializer)
def get_post(id: int) -> dict:
    for post in posts:
        if post.get("id") == id:
            return post
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="post not found!")

@app.post("/api/posts", response_model=PostResponseSerializer, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreateSerializer):
    new_id = max(p["id"] for p in posts) + 1 if posts else 1
    new_post = {
        "id": new_id,
        "title": post.title,
        "content": post.content,
        "date_posted": "April 23, 2025",
    }
    posts.append(new_post)
    return new_post