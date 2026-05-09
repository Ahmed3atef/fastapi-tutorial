from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.settings import app, templates
from fastapi import Depends, Request, HTTPException, status
from db.config import get_db
from db.models import Post, User
from schemas.schema_posts import PostResponseSerializer


@app.get("/posts/{id}", include_in_schema=False)
def post_view(request: Request,
            id: int,
            db: Annotated[Session, Depends(get_db)]
        ):
    res = db.execute(
        select(Post).where(Post.id == id)
    )
    
    post = res.scalars().first()
    if post:
        title = post.title[:50]
        return templates.TemplateResponse(
            request,
            "post.html",
            {
                "post": post,
                "title": title
            }
        )
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

@app.get("/users/{id}/posts",
        include_in_schema=False,
        name="user_posts"
    )
def user_posts_page(
    request: Request,
    id: int,
    db: Annotated[Session, Depends(get_db)]
):
    res = db.execute(
        select(User).where(User.id == id)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    res = db.execute(
        select(Post).where(Post.user_id == id)
    )
    posts = res.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts":posts,
            "user": user.username,
            "title": f"{user.username}'s Posts",
        }
    )
    

@app.get("/api/users/{id}/posts", 
         response_model=list[PostResponseSerializer])
def get_user_posts(id: int, 
                   db: Annotated[Session, Depends(get_db)]):
    
    result = db.execute(select(User).where(User.id == id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = db.execute(select(Post).where(
        Post.user_id == id))
    posts = result.scalars().all()
    return posts
