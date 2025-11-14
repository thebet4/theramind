from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import LoginResponse, ResetPassword
from app.schemas.therapist import TherapistCreate, TherapistLogin, TherapistResponse
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


@router.get("/refresh-token")
def refresh_token(
    therapist: TherapistResponse = Depends(get_current_therapist),
    db: Session = Depends(get_db),
):
    return AuthService.refresh_token(therapist.id, db)


@router.post("/forgot-password")
def forgot_password(email: EmailStr, db: Session = Depends(get_db)):
    print(f"Forgot password request for email: {email}")
    return AuthService.forgot_password(email, db)


@router.post("/reset-password")
def reset_password(token: str, data: ResetPassword, db: Session = Depends(get_db)):
    print(f"Reset password request for token: {token}")
    return AuthService.reset_password(token, data, db)
