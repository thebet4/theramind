import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.therapist import Therapist
from app.schemas.therapist import (
    TherapistLogin,
    TherapistResponse,
)
from app.core.security import verify_password
from app.core.auth import create_access_token
from datetime import datetime, timezone


class AuthService:
    @staticmethod
    def authenticate(data: TherapistLogin, db: Session) -> dict:
        email = data.email
        password = data.password
        therapist = db.query(Therapist).filter_by(email=email).first()
        if not therapist or not verify_password(password, therapist.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return {
            "access_token": create_access_token({"sub": str(therapist.id)}),
            "token_type": "bearer",
            "therapist": TherapistResponse.model_validate(therapist),
        }

    @staticmethod
    def logout(therapist_id: uuid.UUID, db: Session):
        therapist = db.query(Therapist).filter_by(id=therapist_id).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")
        therapist.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(therapist)
        return therapist
