from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.therapist import (
    TherapistCreate,
    TherapistLogin,
    TherapistResponse,
    LoginResponse,
)
from app.services.auth_service import AuthService
from app.services.therapist_service import TherapistService
from app.core.dependencies import get_current_therapist

router = APIRouter()


@router.post("/signup", response_model=TherapistResponse)
def signup(data: TherapistCreate, db: Session = Depends(get_db)):
    return TherapistService.create_therapist(data, db)


@router.post("/login", response_model=LoginResponse)
def login(data: TherapistLogin, db: Session = Depends(get_db)):
    return AuthService.authenticate(data, db)


@router.post("/logout")
def logout(
    therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return AuthService.logout(therapist.id, db)
