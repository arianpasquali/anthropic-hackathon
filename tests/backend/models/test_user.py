import pytest
from sqlmodel import Session, select
from src.backend.models.user import User
from src.backend.models.enums import RoleEnum


def test_create_user(session: Session):
    user = User(
        email="buyer@acme.com",
        hashed_password="hashed_abc",
        role=RoleEnum.corporate,
        org_name="ACME Corp",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.email == "buyer@acme.com"
    assert user.role == RoleEnum.corporate


def test_user_email_unique(session: Session):
    u1 = User(email="dup@test.com", hashed_password="x", role=RoleEnum.corporate)
    u2 = User(email="dup@test.com", hashed_password="y", role=RoleEnum.admin)
    session.add(u1)
    session.commit()
    session.add(u2)
    with pytest.raises(Exception):
        session.commit()


def test_user_role_default(session: Session):
    user = User(email="op@bank.nl", hashed_password="x", role=RoleEnum.foodbank)
    session.add(user)
    session.commit()
    result = session.exec(select(User).where(User.email == "op@bank.nl")).one()
    assert result.role == RoleEnum.foodbank
