from datetime import datetime, timezone
from app.core.database import Base
from sqlalchemy import Boolean, DateTime, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
import uuid


class ProcessingError(Base):
    __tablename__ = "processing_errors"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id"), nullable=False
    )
    job_id: Mapped[str] = mapped_column(String, nullable=False)

    # Error
    error_type: Mapped[str] = mapped_column(String, nullable=False)
    error_message: Mapped[str] = mapped_column(String, nullable=False)
    error_stack: Mapped[str] = mapped_column(String, nullable=False)

    # Retry
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    next_retry_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Context
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    resolved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
