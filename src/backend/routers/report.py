import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.user import User
from src.backend.models.marketplace import FundSubscription
from src.backend.services.auth import get_current_user
from src.backend.services.report import get_report_path, stream_report

router = APIRouter(prefix="/report", tags=["report"])


def _get_owned_sub(sub_id: uuid.UUID, session: Session, user: User) -> FundSubscription:
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    return sub


@router.post("/{sub_id}/generate")
def generate_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    return {"sub_id": str(sub_id), "stream_url": f"/report/{sub_id}/stream"}


@router.get("/{sub_id}/stream")
async def stream_report_sse(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    return StreamingResponse(
        stream_report(session, sub_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{sub_id}/download")
def download_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    path = get_report_path(session, sub_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Report not yet generated")
    return FileResponse(path, media_type="text/markdown", filename=f"csrd-report-{sub_id}.md")
