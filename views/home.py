
from typing import Annotated
from fastapi.params import Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from core.settings import app, templates
from fastapi import Request
from db.config import get_db
from db.models import Post

@app.get("/", include_in_schema=False, name="home")
@app.get("/posts", include_in_schema=False, name="posts")
def root(request: Request,
        db: Annotated[Session, Depends(get_db)]
    ):
    
    res = db.execute(
        select(Post)
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
