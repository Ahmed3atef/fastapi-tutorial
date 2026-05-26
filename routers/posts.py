from main import (
    AsyncSession,
    selectinload,
    Annotated,
    select,
    status,
    APIRouter,
    Depends,
    get_db,
    Post,
    HTTPException,
    User
)

from schemas import PostCreateSerializer,PostUpdateSerializer,PostResponseSerializer

router = APIRouter()


@router.get("", response_model=list[PostResponseSerializer])
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
    )
    posts = result.scalars().all()
    return posts


@router.post("", response_model=PostResponseSerializer, status_code=status.HTTP_201_CREATED,)
async def create_post(post: PostCreateSerializer, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User)
        .where(
            User.id == post.user_id)
    )
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
    await db.commit()
    await db.refresh(new_post, attribute_names=["author"])
    return new_post


@router.get("/{id}", response_model=PostResponseSerializer)
async def get_post(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id))
    post = result.scalars().first()
    if post:
        return post
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Post not found"
    )


@router.put("/{id}", response_model=PostResponseSerializer)
async def update_post_full(id: int, data: PostCreateSerializer, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if data.user_id != post.user_id:
        result = await db.execute(
            select(User)
            .where(User.id == data.user_id)
        )
        user = result.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

    post.title = data.title
    post.content = data.content
    post.user_id = data.user_id

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{id}", response_model=PostResponseSerializer)
async def update_post_partial(id: int, data: PostUpdateSerializer, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    await db.delete(post)
    await db.commit()
