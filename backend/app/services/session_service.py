from datetime import datetime, timezone
from typing import Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
import math

from app.models.session import Session as SessionModel
from app.models.patient import Patient
from app.schemas.session import (
    SessionCreate,
    SessionResponse,
    SessionFilter,
    PaginatedSessionResponse,
    SessionUpdate,
    UploadUrlRequest,
    UploadUrlResponse,
)
from app.core.aws import aws_service


class SessionService:
    @staticmethod
    def generate_upload_url(
        therapist_id: uuid.UUID, request: UploadUrlRequest, db: Session
    ) -> UploadUrlResponse:
        # Verify patient belongs to therapist
        patient = (
            db.query(Patient)
            .filter_by(
                id=request.patient_id, therapist_id=therapist_id, is_deleted=False
            )
            .first()
        )

        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found or you don't have permission to access it",
            )

        # Validate file type
        allowed_types = ["audio/mpeg", "audio/wav", "audio/x-m4a", "audio/mp3"]
        if request.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid content type. Allowed types: {', '.join(allowed_types)}",
            )

        # Generate presigned URL
        try:
            presigned_url, s3_key = aws_service.generate_presigned_url(
                file_name=request.file_name, content_type=request.content_type
            )

            return UploadUrlResponse(
                upload_url=presigned_url,
                s3_key=s3_key,
                expires_in=900,  # 15 minutes
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Error generating upload URL: {str(e)}"
            )

    @staticmethod
    def create_session(
        therapist_id: uuid.UUID, session_data: SessionCreate, s3_key: str, db: Session
    ) -> SessionResponse:
        # Verify patient belongs to therapist
        patient = (
            db.query(Patient)
            .filter_by(
                id=session_data.patient_id,
                therapist_id=therapist_id,
                is_deleted=False,
            )
            .first()
        )

        if not patient:
            raise HTTPException(
                status_code=404,
                detail="Patient not found or you don't have permission to access it",
            )

        # Verify S3 file exists
        if not aws_service.check_file_exists(s3_key):
            raise HTTPException(
                status_code=400,
                detail="Audio file not found in storage. Please upload again.",
            )

        # Create session record
        new_session = SessionModel(
            therapist_id=therapist_id,
            patient_id=session_data.patient_id,
            session_date=session_data.session_date,
            s3_audio_key=s3_key,
            audio_metadata=session_data.audio_metadata,
            processing_status="pending",
        )

        db.add(new_session)
        db.commit()
        db.refresh(new_session)

        # Send job to SQS queue
        try:
            job_id = aws_service.send_processing_job(
                session_id=str(new_session.id),
                therapist_id=str(therapist_id),
                patient_id=str(session_data.patient_id),
                s3_key=s3_key,
                audio_metadata=session_data.audio_metadata,
            )

            if job_id:
                new_session.job_id = job_id
                db.commit()
                db.refresh(new_session)
            else:
                # If job creation fails, mark session as failed
                new_session.processing_status = "failed"
                db.commit()
                raise HTTPException(
                    status_code=500,
                    detail="Failed to enqueue processing job. Session created but not queued.",
                )

        except Exception as e:
            new_session.processing_status = "failed"
            db.commit()
            raise HTTPException(
                status_code=500, detail=f"Error creating processing job: {str(e)}"
            )

        return SessionResponse.model_validate(new_session)

    @staticmethod
    def get_sessions(
        therapist_id: uuid.UUID,
        db: Session,
        page: int = 1,
        page_size: int = 10,
        filters: Optional[SessionFilter] = None,
    ) -> PaginatedSessionResponse:
        query = db.query(SessionModel).filter(
            SessionModel.therapist_id == therapist_id, SessionModel.is_deleted == False
        )

        # Apply filters
        if filters:
            if filters.patient_id:
                query = query.filter(SessionModel.patient_id == filters.patient_id)

            if filters.processing_status:
                query = query.filter(
                    SessionModel.processing_status == filters.processing_status
                )

            if filters.session_date_from:
                query = query.filter(
                    SessionModel.session_date >= filters.session_date_from
                )

            if filters.session_date_to:
                query = query.filter(
                    SessionModel.session_date <= filters.session_date_to
                )

        # Get total count
        total = query.count()
        total_pages = math.ceil(total / page_size) if total > 0 else 0

        # Paginate
        offset = (page - 1) * page_size
        sessions = (
            query.order_by(SessionModel.session_date.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        return PaginatedSessionResponse(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            sessions=[SessionResponse.model_validate(session) for session in sessions],
        )

    @staticmethod
    def get_session_by_id(
        therapist_id: uuid.UUID, session_id: uuid.UUID, db: Session
    ) -> SessionResponse:
        session = (
            db.query(SessionModel)
            .filter_by(id=session_id, therapist_id=therapist_id, is_deleted=False)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or you don't have permission to access it",
            )

        return SessionResponse.model_validate(session)

    @staticmethod
    def update_session(
        therapist_id: uuid.UUID,
        session_id: uuid.UUID,
        update_data: SessionUpdate,
        db: Session,
    ) -> SessionResponse:
        session = (
            db.query(SessionModel)
            .filter_by(id=session_id, therapist_id=therapist_id, is_deleted=False)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or you don't have permission to access it",
            )

        # Update fields if provided
        if update_data.processing_status:
            session.processing_status = update_data.processing_status

        if update_data.session_duration_minutes:
            session.session_duration_minutes = update_data.session_duration_minutes

        if update_data.summary:
            session.summary = update_data.summary
            session.version += 1

        session.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(session)

        return SessionResponse.model_validate(session)

    @staticmethod
    def delete_session(
        therapist_id: uuid.UUID, session_id: uuid.UUID, db: Session
    ) -> dict:
        session = (
            db.query(SessionModel)
            .filter_by(id=session_id, therapist_id=therapist_id, is_deleted=False)
            .first()
        )

        if not session:
            raise HTTPException(
                status_code=404,
                detail="Session not found or you don't have permission to access it",
            )

        # Soft delete
        session.is_deleted = True
        session.deleted_at = datetime.now(timezone.utc)

        # Delete audio file from S3 if it still exists
        if session.s3_audio_key:
            aws_service.delete_audio_file(session.s3_audio_key)

        db.commit()

        return {"message": "Session deleted successfully"}
