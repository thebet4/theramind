from datetime import datetime
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from app.core.dependencies import get_current_therapist
from app.core.database import get_db
from app.schemas.therapist import TherapistResponse
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionFilter,
    PaginatedSessionResponse,
    SessionUpdate,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/upload-url", response_model=UploadUrlResponse)
def generate_upload_url(
    request: UploadUrlRequest,
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return SessionService.generate_upload_url(current_therapist.id, request, db)


@router.post("", response_model=SessionResponse, status_code=201)
def create_session(
    session_data: SessionCreate,
    s3_key: str = Query(..., description="S3 key where audio file was uploaded"),
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return SessionService.create_session(current_therapist.id, session_data, s3_key, db)


@router.get("", response_model=PaginatedSessionResponse)
def list_sessions(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    patient_id: Optional[uuid.UUID] = Query(None, description="Filter by patient ID"),
    processing_status: Optional[str] = Query(
        None,
        description="Filter by status (pending, processing, completed, failed, cancelled)",
    ),
    session_date_from: Optional[str] = Query(
        None, description="Filter sessions from this date (ISO format)"
    ),
    session_date_to: Optional[str] = Query(
        None, description="Filter sessions up to this date (ISO format)"
    ),
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    filters = SessionFilter(
        patient_id=patient_id,
        processing_status=processing_status,
        session_date_from=(
            datetime.fromisoformat(session_date_from) if session_date_from else None
        ),
        session_date_to=(
            datetime.fromisoformat(session_date_to) if session_date_to else None
        ),
    )

    return SessionService.get_sessions(
        current_therapist.id, db, page, page_size, filters
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(
    session_id: uuid.UUID,
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return SessionService.get_session_by_id(current_therapist.id, session_id, db)


@router.patch("/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: uuid.UUID,
    update_data: SessionUpdate,
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return SessionService.update_session(
        current_therapist.id, session_id, update_data, db
    )


@router.delete("/{session_id}")
def delete_session(
    session_id: uuid.UUID,
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return SessionService.delete_session(current_therapist.id, session_id, db)
