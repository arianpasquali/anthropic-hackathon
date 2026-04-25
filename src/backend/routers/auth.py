import uuid
from typing import Optional

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import RoleEnum
from src.backend.models.user import User
from src.backend.services.auth import (
    COOKIE_NAME,
    decode_session_cookie,
    get_current_user,
    hash_password,
    make_session_cookie,
    verify_password,
)

router = APIRouter(prefix="/auth")


class RegisterRequest(BaseModel):
    email: str
    password: str
    org_name: str
    role: RoleEnum = RoleEnum.corporate


class LoginRequest(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    org_name: Optional[str]
    role: str


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def register(body: RegisterRequest, session: Session = Depends(get_session)):
    existing = session.exec(select(User).where(User.email == body.email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        role=body.role,
        org_name=body.org_name,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse(id=str(user.id), email=user.email, org_name=user.org_name, role=user.role.value)


@router.post("/login", response_model=UserResponse)
def login(body: LoginRequest, response: Response, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    response.set_cookie(COOKIE_NAME, make_session_cookie(str(user.id)), httponly=True, samesite="lax")
    return UserResponse(id=str(user.id), email=user.email, org_name=user.org_name, role=user.role.value)


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"ok": True}


@router.get("/me", response_model=UserResponse)
def me(user: User = Depends(get_current_user)):
    return UserResponse(id=str(user.id), email=user.email, org_name=user.org_name, role=user.role.value)
