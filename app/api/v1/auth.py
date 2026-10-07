from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import ConflictException, NotAuthenticatedException
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserResponse, UserCreate

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Register a new user")
async def register(payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> User:
    existing_user_query = select(User).where(User.email == payload.email)
    result = await db.execute(existing_user_query)
    if result.scalar_one_or_none():
        raise ConflictException("A user with this email already exists")

    new_user = User(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login", summary="Login with email and password to receive a JWT access token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, str]:
    query = select(User).where(User.email == form_data.username)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user in None or not verify_password(form_data.password, user.hashed_password):
        raise NotAuthenticatedException()

    access_token = create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}