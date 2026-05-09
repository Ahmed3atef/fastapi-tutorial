from core import app
from fastapi import status, HTTPException, Depends
from db.config import get_db
from db.models import User, Post
from schemas.schema_posts import PostResponseSerializer
from schemas.schema_users import UserResponseSerializer, UserCreateSerializer
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session



@app.post("/api/users", 
        response_model=UserResponseSerializer, 
        status_code=status.HTTP_201_CREATED
    )
def create_user(user: UserCreateSerializer, 
            db: Annotated[Session, Depends(get_db)]
        ):
    
    res_username = db.execute(select(User).where(User.username == user.username),)
    res_email = db.execute(select(User).where(User.email == user.email))
    existing_user_username = res_username.scalars().first()
    existing_user_email = res_email.scalars().first()
    
    if existing_user_username:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail= "Username already exists",
        )
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
        
    new_user = User(
        username = user.username,
        email = user.email,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user
    

@app.get("/api/users/{id}",
        response_model=UserResponseSerializer,
        status_code= status.HTTP_200_OK
    )
def get_user(id: int,
         db: Annotated[Session, Depends(get_db)]
    ):
    
    res = db.execute(
        select(User).where(User.id == id)
    )
    
    user = res.scalars().first()
    
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/api/users/{id}/posts",
        response_model=list[PostResponseSerializer]
        )
def get_user_posts(id: int,
                   db: Annotated[Session, Depends(get_db)]
                ):
    
    res = db.execute(
        select(User).where(User.id == id)
    )
    user = res.scalars().first()
    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    res = db.execute(
        select(Post).where(Post.user_id == id)
    )
    posts = res.scalars().all()
    return posts
