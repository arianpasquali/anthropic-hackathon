import os
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.user import User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-prod")
_signer = URLSafeTimedSerializer(_SECRET)
COOKIE_NAME = "session"


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def make_session_cookie(user_id: str) -> str:
    return _signer.dumps(user_id)


def decode_session_cookie(token: str) -> Optional[str]:
    try:
        return _signer.loads(token, max_age=86400 * 7)
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(
    session: Session = Depends(get_session),
    session_cookie: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> User:
    if not session_cookie:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    user_id = decode_session_cookie(session_cookie)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    from src.backend.models.enums import RoleEnum
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=403)
    return user
