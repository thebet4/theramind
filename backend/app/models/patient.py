from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional, List
from sqlalchemy import String, ForeignKey, UniqueConstraint, DateTime, Boolean
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.therapist import Therapist
    from app.models.session import Session


class Patient(Base):
    __tablename__ = "patients"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    # Basic data
    identifier: Mapped[str] = mapped_column(String, nullable=False)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Consent
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_timestamp: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    consent_ip: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship to Therapist
    therapist_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("therapists.id"), nullable=False
    )
    therapist: Mapped["Therapist"] = relationship(
        "Therapist", back_populates="patients"
    )

    # Relationships to sessions
    sessions: Mapped[List["Session"]] = relationship(
        "Session", back_populates="patient"
    )

    # Unique constraint per therapist
    __table_args__ = (
        UniqueConstraint(
            "therapist_id", "identifier", name="unique_patient_per_therapist"
        ),
    )

    def __repr__(self) -> str:
        return f"<Patient id={self.id} identifier={self.identifier} therapist_id={self.therapist_id}>"
