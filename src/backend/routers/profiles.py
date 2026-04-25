import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.profile import ImpactProfile
from src.backend.models.user import User
from src.backend.services.auth import get_current_user, require_admin

router = APIRouter(prefix="/profiles", tags=["profiles"])


class ProfileResponse(BaseModel):
    id: str
    key: str
    name: str
    description: Optional[str]
    co2_weight: float
    social_weight: float
    is_active: bool


class ProfileCreate(BaseModel):
    key: str
    name: str
    description: Optional[str] = None
    co2_weight: float = 0.5
    social_weight: float = 0.5

    @field_validator("co2_weight", "social_weight")
    @classmethod
    def weight_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")
        return v


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    co2_weight: Optional[float] = None
    social_weight: Optional[float] = None
    is_active: Optional[bool] = None

    @field_validator("co2_weight", "social_weight")
    @classmethod
    def weight_range(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and not 0.0 <= v <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")
        return v


def _to_response(p: ImpactProfile) -> ProfileResponse:
    return ProfileResponse(
        id=str(p.id),
        key=p.key,
        name=p.name,
        description=p.description,
        co2_weight=p.co2_weight,
        social_weight=p.social_weight,
        is_active=p.is_active,
    )


@router.get("", response_model=list[ProfileResponse])
def list_profiles(
    include_inactive: bool = False,
    session: Session = Depends(get_session),
):
    q = select(ImpactProfile)
    if not include_inactive:
        q = q.where(ImpactProfile.is_active == True)
    return [_to_response(p) for p in session.exec(q).all()]


@router.get("/{key}", response_model=ProfileResponse)
def get_profile(key: str, session: Session = Depends(get_session)):
    profile = session.exec(select(ImpactProfile).where(ImpactProfile.key == key)).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{key}' not found")
    return _to_response(profile)


@router.post("", response_model=ProfileResponse, status_code=201)
def create_profile(
    body: ProfileCreate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    existing = session.exec(select(ImpactProfile).where(ImpactProfile.key == body.key)).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Profile key '{body.key}' already exists")
    profile = ImpactProfile(**body.model_dump())
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return _to_response(profile)


@router.put("/{key}", response_model=ProfileResponse)
def update_profile(
    key: str,
    body: ProfileUpdate,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    profile = session.exec(select(ImpactProfile).where(ImpactProfile.key == key)).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{key}' not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return _to_response(profile)


@router.delete("/{key}", status_code=204)
def delete_profile(
    key: str,
    session: Session = Depends(get_session),
    _user: User = Depends(require_admin),
):
    profile = session.exec(select(ImpactProfile).where(ImpactProfile.key == key)).first()
    if not profile:
        raise HTTPException(status_code=404, detail=f"Profile '{key}' not found")
    profile.is_active = False
    session.add(profile)
    session.commit()
