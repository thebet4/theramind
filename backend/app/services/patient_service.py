from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import uuid
import math
from app.schemas.patient import (
    PatientCreate,
    PatientResponse,
    PatientFilter,
    PaginatedPatientResponse,
)
from app.models.patient import Patient


class PatientService:
    @staticmethod
    def get_patients(
        therapist_id: uuid.UUID,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[PatientFilter] = None,
    ) -> PaginatedPatientResponse:
        query = db.query(Patient).filter(
            Patient.therapist_id == therapist_id, Patient.is_deleted == False
        )

        if filters:
            if filters.identifier:
                query = query.filter(
                    Patient.identifier.ilike(f"%{filters.identifier}%")
                )

            if filters.consent_given is not None:
                query = query.filter(Patient.consent_given == filters.consent_given)

            if filters.created_after:
                query = query.filter(Patient.created_at >= filters.created_after)

            if filters.created_before:
                query = query.filter(Patient.created_at <= filters.created_before)

        total = query.count()

        total_pages = math.ceil(total / page_size) if total > 0 else 0
        offset = (page - 1) * page_size

        patients = (
            query.order_by(Patient.created_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return PaginatedPatientResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            patients=[PatientResponse.model_validate(patient) for patient in patients],
        )

    @staticmethod
    def create_patient(
        therapist_id: uuid.UUID, patient: PatientCreate, db: Session
    ) -> PatientResponse:
        existing = (
            db.query(Patient)
            .filter_by(identifier=patient.identifier, therapist_id=therapist_id)
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Patient with this identifier already exists"
            )
        new_patient = Patient(
            identifier=patient.identifier,
            date_of_birth=patient.date_of_birth,
            therapist_id=therapist_id,
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return PatientResponse.model_validate(new_patient)
