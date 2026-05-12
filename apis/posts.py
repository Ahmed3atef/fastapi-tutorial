from core import app
from fastapi import status, HTTPException, Depends
from db.models import Post, User
from db.config import get_db
from typing import Annotated
from sqlalchemy import select
from sqlalchemy.orm import Session
from schemas import PostResponseSerializer, PostCreateSerializer, PostUpdateSerializer
from schemas.schema_posts import PostSerializer


@app.get("/api/posts", response_model=list[PostResponseSerializer])
def get_posts(db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post))
    posts = result.scalars().all()
    return posts


@app.post(
    "/api/posts",
    response_model=PostResponseSerializer,
    status_code=status.HTTP_201_CREATED,
)
def create_post(post: PostCreateSerializer,
            db: Annotated[Session, Depends(get_db)]
        ):
    result = db.execute(select(User).where(
        User.id == post.user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@app.get("/api/posts/{id}", response_model=PostResponseSerializer)
def get_post(id: int, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(select(Post).where(Post.id == id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
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

@app.put("/api/posts/{id}", response_model=PostResponseSerializer)
def update_post_full(id:int,
                    data: PostCreateSerializer,
                    db:Annotated[Session, Depends(get_db)]):
    res = db.execute(
        select(Post).where(Post.id == id)
    )
    post = res.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if data.user_id != post.user_id:
        result = db.execute(select(User).where(User.id == data.user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
            
    post.title = data.title
    post.content = data.content
    post.user_id = data.user_id
    
    db.commit()
    db.refresh(post)
    return post


@app.patch("/api/posts/{id}", response_model=PostResponseSerializer)
def update_post_partial(id: int,
                     data: PostUpdateSerializer,
                     db: Annotated[Session, Depends(get_db)]):
    res = db.execute(
        select(Post).where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    return post


@app.delete("/api/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Annotated[Session, Depends(get_db)]):
    res = db.execute(
        select(Post).where(Post.id == id)
    )
    post = res.scalars().first()
    
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    db.delete(post)
    db.commit()
    
    