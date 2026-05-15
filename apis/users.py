from core.settings import app, AsyncSession, selectinload
from fastapi import status, HTTPException, Depends
from db import get_db, User, Post
from schemas import UserResponseSerializer, UserCreateSerializer, UserUpdateSerializer, PostResponseSerializer
from typing import Annotated
from sqlalchemy import select



@app.post("/api/users",response_model=UserResponseSerializer,status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSerializer,db: Annotated[AsyncSession, Depends(get_db)]):
    res_username = await db.execute(
        select(User)
        .where(
            User.username == user.username)
        )
    res_email = await db.execute(
        select(User)
        .where(User.email == user.email)
        )
    existing_user_username = res_username.scalars().first()
    existing_user_email = res_email.scalars().first()

    if existing_user_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    if existing_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )

    new_user = User(
        username=user.username,
        email=user.email,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@app.get("/api/users/{id}",response_model=UserResponseSerializer,status_code=status.HTTP_200_OK)
async def get_user(id: int,db: Annotated[AsyncSession, Depends(get_db)]):

    res = await db.execute(
        select(User)
        .where(User.id == id)
    )

    user = res.scalars().first()

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found")


@app.patch("/api/users/{id}", response_model=UserResponseSerializer)
async def update_user(id: int,data: UserUpdateSerializer,db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(User).where(User.id == id))
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.username is not None and data.username != user.username:
        res = await db.execute(
            select(User)
            .where(User.username == data.username),
        )
        existing_user = res.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if data.email is not None and data.email != user.email:
        res = await db.execute(
            select(User)
            .where(User.email == data.email),
        )
        existing_user = res.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email already exists",
            )

    # if data.username is not None:
    #     user.username = data.username
    # if data.email is not None:
    #     user.email = data.email
    # if data.image_file is not None:
    #     user.image_file = data.image_file

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@app.delete("/api/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(User)
        .where(User.id == id)
    )
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user)
    await db.commit()


@app.get("/api/users/{id}/posts",response_model=list[PostResponseSerializer])
async def get_user_posts(id: int,db: Annotated[AsyncSession, Depends(get_db)]):

    result = await db.execute(
        select(User)
        .where(User.id == id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.user_id == id)
    )
    posts = result.scalars().all()
    return posts
