from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.foodbank import Foodbank
from src.backend.models.user import User
from src.backend.services.auth import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


class FoodbankResponse(BaseModel):
    id: str
    name: str
    city: str
    region: str
    is_regional_dc: bool


@router.get("/foodbanks", response_model=list[FoodbankResponse])
def list_foodbanks(session: Session = Depends(get_session), user: User = Depends(require_admin)):
    banks = session.exec(select(Foodbank)).all()
    return [FoodbankResponse(id=str(fb.id), name=fb.name, city=fb.city,
                              region=fb.region.value, is_regional_dc=fb.is_regional_dc)
            for fb in banks]
