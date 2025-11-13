from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import datetime
from app.core.dependencies import get_current_therapist
from app.core.database import get_db
from app.schemas.therapist import TherapistResponse
from app.schemas.patient import PatientCreate, PaginatedPatientResponse, PatientFilter
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.get("/", response_model=PaginatedPatientResponse)
def list_patients(
    db: Session = Depends(get_db),
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    identifier: Optional[str] = Query(None, description="Search by patient identifier"),
    consent_given: Optional[bool] = Query(None, description="Filter by consent status"),
    created_after: Optional[datetime.datetime] = Query(
        None, description="Filter patients created after this date"
    ),
    created_before: Optional[datetime.datetime] = Query(
        None, description="Filter patients created before this date"
    ),
):
    filters = PatientFilter(
        identifier=identifier,
        consent_given=consent_given,
        created_after=created_after,
        created_before=created_before,
    )
    return PatientService.get_patients(
        therapist_id=current_therapist.id,
        db=db,
        page=page,
        page_size=page_size,
        filters=filters,
    )


@router.post("/")
def create_patient(
    db: Session = Depends(get_db),
    current_therapist: TherapistResponse = Depends(get_current_therapist),
    patient: PatientCreate = Body(...),
):
    return PatientService.create_patient(current_therapist.id, patient, db)
