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

from utils.auth import CurrentUser, get_current_user

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
async def create_post(
    post: PostCreateSerializer,
    current_user: CurrentUser, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    
    
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=current_user.id,
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
async def update_post_full(
    id: int, 
    current_user: CurrentUser,
    data: PostCreateSerializer, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to update this post",
        )

    post.title = data.title
    post.content = data.content
    post.user_id = current_user.id

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.patch("/{id}", response_model=PostResponseSerializer)
async def update_post_partial(
    id: int, 
    current_user: CurrentUser,
    data: PostUpdateSerializer, 
    db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)

    await db.commit()
    await db.refresh(post, attribute_names=["author"])
    return post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    id: int, 
    current_user: CurrentUser,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    res = await db.execute(
        select(Post)
        .options(selectinload(Post.author))
        .where(Post.id == id)
    )
    post = res.scalars().first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    await db.delete(post)
    await db.commit()
