from typing import Annotated
from sqlalchemy import select
from core.settings import app, templates, AsyncSession, selectinload
from fastapi import Depends, Request, HTTPException, status
from db import Post, User, get_db


@app.get("/posts/{id}", include_in_schema=False)
async def post_view(request: Request,
            id: int,
            db: Annotated[AsyncSession, Depends(get_db)]
        ):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
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
async def user_posts_page(
    request: Request,
    id: int,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(
        select(User)
        .where(User.id == id)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.user_id == id)
    )
    posts = res.scalars().all()
    return templates.TemplateResponse(
        request,
        "user_posts.html",
        {
            "posts":posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        }
    )
    
