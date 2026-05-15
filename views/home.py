
from typing import Annotated
from fastapi.params import Depends
from sqlalchemy import select
from core.settings import app, templates, AsyncSession, selectinload
from fastapi import Request
from db.config import get_db
from db.models import Post


@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
async def root(request: Request,
         db: Annotated[AsyncSession, Depends(get_db)]
         ):

    res = await db.execute(
        select(Post).options(selectinload(Post.author))
    )
    posts = res.scalars().all()
    return templates.TemplateResponse(
        request,
        "home.html",
        {
            "posts": posts,
            "title": "Home"
        }
    )
