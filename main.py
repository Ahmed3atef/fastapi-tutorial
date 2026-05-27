from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi import FastAPI, status, HTTPException, Depends, APIRouter, Request
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from db import Base, engine,  get_db, User, Post
import logging
from routers import posts, users


logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        # Startup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield

        # Shutdown
        await engine.dispose()
    except Exception as e:
        logger.error(f"Could not connect to database: {e}")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

templates = Jinja2Templates(directory="templates")

app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])


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

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Post not found")


@app.get("/users/{id}/posts",include_in_schema=False,name="user_posts")
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
            "posts": posts,
            "user": user,
            "title": f"{user.username}'s Posts",
        }
    )


@app.get("/login", include_in_schema=False)
async def login_page(request: Request):
    return templates.TemplateResponse(
        request,
        "login.html",
        {
            "title": "Login",
        }
    )
    
@app.get("/register", include_in_schema=False)
async def register_page(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {
            "title": "Register",
        }
    )