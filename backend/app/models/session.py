from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    DateTime,
    Integer,
    String,
    Boolean,
    Index,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

import uuid
from datetime import datetime, timezone

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.therapist import Therapist


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    therapist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("therapists.id"), nullable=False
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False
    )

    # Relationships (string references to avoid circular imports)
    therapist: Mapped["Therapist"] = relationship(
        "Therapist", back_populates="sessions"
    )
    patient: Mapped["Patient"] = relationship("Patient", back_populates="sessions")

    # Session data
    session_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    session_duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Processing
    processing_status: Mapped[str] = mapped_column(
        String, nullable=False, default="pending"
    )
    job_id: Mapped[str] = mapped_column(String, nullable=False)

    # Metadata
    audio_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False)
    summary: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processing_started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    processing_completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Soft delete
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Versioning
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    def __repr__(self) -> str:
        return f"<Session id={self.id} therapist={self.therapist_id} patient={self.patient_id}>"


Index("idx_sessions_therapist", Session.therapist_id)
Index("idx_sessions_patient", Session.patient_id)
Index("idx_sessions_date", Session.session_date)
Index(
    "idx_sessions_status",
    Session.processing_status,
    postgresql_where=Session.processing_status != "completed",
)
