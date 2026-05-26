from main import(
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
from schemas import UserPublicSerializer, UserPrivateSerializer, UserCreateSerializer, UserUpdateSerializer, PostResponseSerializer, TokenSerializer

from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from utils.auth import (
    create_access_token, 
    hash_password, 
    oauth2_schema, 
    verify_access_token,
    verify_password
)
from config import settings

router = APIRouter()

@router.post("", response_model=UserPrivateSerializer, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSerializer, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(
        select(User).where(
            func.lower(User.username) == user.username.lower(),
        ),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    result = await db.execute(
        select(User).where(func.lower(User.email) == user.email.lower()),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    new_user = User(
        username=user.username,
        email=user.email.lower(),
        password_hash=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/token", response_model=TokenSerializer)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Look up user by email (case-insensitive)
    # Note: OAuth2PasswordRequestForm uses "username" field, but we treat it as email
    result = await db.execute(
        select(User).where(
            func.lower(User.email) == form_data.username.lower(),
        ),
    )
    user = result.scalars().first()

    # Verify user exists and password is correct
    # Don't reveal which one failed (security best practice)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token with user id as subject
    access_token_expires = timedelta(
        minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    return TokenSerializer(access_token=access_token, token_type="bearer")

@router.get("/me", response_model=UserPrivateSerializer, status_code=status.HTTP_200_OK)
async def get_current_user(
    token: Annotated[str, Depends(oauth2_schema)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Get the currently authenticated user."""
    user_id = verify_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate user_id is valid integer 
    try:
        user_id_int = int(user_id)
    except(TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    result = await db.execute(
        select(User).
        where(
            User.id == user_id_int
        ),
    )
    
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user

@router.get("/{id}", response_model=UserPublicSerializer, status_code=status.HTTP_200_OK)
async def get_user(id: int, db: Annotated[AsyncSession, Depends(get_db)]):

    res = await db.execute(
        select(User)
        .where(User.id == id)
    )

    user = res.scalars().first()

    if user:
        return user

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found")


@router.patch("/{id}", response_model=UserPrivateSerializer)
async def update_user(id: int, data: UserUpdateSerializer, db: Annotated[AsyncSession, Depends(get_db)]):
    res = await db.execute(select(User).where(User.id == id))
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if data.username is not None and data.username.lower() != user.username.lower():
        res = await db.execute(
            select(User)
            .where(
                func.lower(User.username) == data.username.lower()
            ),
        )
        existing_user = res.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists",
            )
    if data.email is not None and data.email.lower() != user.email.lower():
        res = await db.execute(
            select(User)
            .where(
                func.lower(User.email) == data.email.lower()
            ),
        )
        existing_user = res.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="email already exists",
            )

    if data.username is not None:
        user.username = data.username
    if data.email is not None:
        user.email = data.email.lower()
    if data.image_file is not None:
        user.image_file = data.image_file

    # update_data = data.model_dump(exclude_unset=True)
    # for field, value in update_data.items():
    #     setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
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


@router.get("/{id}/posts", response_model=list[PostResponseSerializer])
async def get_user_posts(id: int, db: Annotated[AsyncSession, Depends(get_db)]):

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
