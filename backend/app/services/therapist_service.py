import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.therapist import Therapist
from app.schemas.therapist import (
    TherapistCreate,
    TherapistResponse,
    TherapistBase,
)
from app.core.security import get_password_hash


class TherapistService:
    @staticmethod
    def create_therapist(data: TherapistCreate, db: Session) -> Therapist:
        existing = db.query(Therapist).filter_by(email=data.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_pw = get_password_hash(data.password)
        new_therapist = Therapist(
            full_name=data.full_name,
            email=data.email,
            professional_license=data.professional_license,
            hashed_password=hashed_pw,
        )
        db.add(new_therapist)
        db.commit()
        db.refresh(new_therapist)
        return new_therapist

    @staticmethod
    def get_by_id(therapist_id: uuid.UUID, db: Session) -> TherapistResponse:
        therapist = db.query(Therapist).filter_by(id=therapist_id).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")
        return TherapistResponse.model_validate(therapist)

    @staticmethod
    def update_therapist(
        therapist_id: uuid.UUID, data: TherapistBase, db: Session
    ) -> TherapistResponse:
        therapist = db.query(Therapist).filter_by(id=therapist_id).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")
        if data.full_name:
            therapist.full_name = data.full_name
        if data.professional_license:
            therapist.professional_license = data.professional_license
        if data.email:
            therapist.email = data.email
        db.commit()
        db.refresh(therapist)
        return TherapistResponse.model_validate(therapist)

    @staticmethod
    def delete_therapist(therapist_id: uuid.UUID, db: Session) -> None:
        therapist = db.query(Therapist).filter_by(id=therapist_id).first()
        if not therapist:
            raise HTTPException(status_code=404, detail="Therapist not found")
        db.delete(therapist)
        db.commit()
