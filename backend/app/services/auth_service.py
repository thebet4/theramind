import uuid
from pydantic import EmailStr
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.therapist import Therapist
from app.schemas.auth import ResetPassword
from app.schemas.therapist import (
    TherapistLogin,
    TherapistResponse,
)
from app.core.security import get_password_hash, verify_password
from app.core.auth import create_access_token
from datetime import datetime, timedelta, timezone


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

        therapist.last_login_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(therapist)

        return {
            "access_token": create_access_token({"sub": str(therapist.id)}),
            "token_type": "Bearer",
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

    @staticmethod
    def refresh_token(therapist_id: uuid.UUID, db: Session):
        therapist = db.query(Therapist).filter_by(id=therapist_id).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")
        return {
            "token_type": "Bearer",
            "access_token": create_access_token({"sub": str(therapist.id)}),
        }

    @staticmethod
    def forgot_password(email: EmailStr, db: Session):
        therapist = db.query(Therapist).filter_by(email=email).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")

        therapist.password_reset_token = str(uuid.uuid4())
        therapist.password_reset_token_expires_at = datetime.now(
            timezone.utc
        ) + timedelta(minutes=15)
        db.commit()
        db.refresh(therapist)

        return {
            "message": "Password reset email sent",
        }

    @staticmethod
    def reset_password(token: str, data: ResetPassword, db: Session):
        therapist = db.query(Therapist).filter_by(password_reset_token=token).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Invalid or expired token")

        if (
            therapist.password_reset_token_expires_at
            and therapist.password_reset_token_expires_at < datetime.now(timezone.utc)
        ):
            raise HTTPException(status_code=400, detail="Token expired")

        therapist.hashed_password = get_password_hash(data.new_password)
        therapist.password_reset_token = None
        therapist.password_reset_token_expires_at = None
        db.commit()
        db.refresh(therapist)
        return {
            "message": "Password reset successfully",
        }
