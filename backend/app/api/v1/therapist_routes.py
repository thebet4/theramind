from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.therapist import (
    TherapistResponse,
    TherapistBase,
)
from app.core.dependencies import get_current_therapist
from app.services.therapist_service import TherapistService

router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/", response_model=TherapistResponse)
def me(
    therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return therapist


@router.put("/", response_model=TherapistResponse)
def update_therapist(
    therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
    data: TherapistBase = Body(...),
):
    return TherapistService.update_therapist(therapist.id, data, db)


@router.delete("/", response_model=None)
def delete_therapist(
    therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return TherapistService.delete_therapist(therapist.id, db)
