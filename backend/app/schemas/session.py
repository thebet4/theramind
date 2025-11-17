import datetime
from typing import Optional, List, Dict, Any
import uuid
from pydantic import BaseModel, Field


# Base schemas for sessions
class SessionBase(BaseModel):
    session_date: datetime.datetime
    patient_id: uuid.UUID


class SessionCreate(SessionBase):
    audio_metadata: Optional[Dict[str, Any]] = Field(
        None, description="Metadata about the uploaded audio file"
    )


class UploadUrlRequest(BaseModel):
    patient_id: uuid.UUID
    file_name: str = Field(..., description="Original file name with extension")
    file_size: int = Field(
        ..., gt=0, lt=100 * 1024 * 1024, description="File size in bytes (max 100MB)"
    )
    content_type: str = Field(
        ..., description="MIME type (e.g., audio/mpeg, audio/wav, audio/x-m4a)"
    )


class UploadUrlResponse(BaseModel):
    upload_url: str = Field(..., description="Presigned S3 URL for direct upload")
    s3_key: str = Field(..., description="S3 object key for the audio file")
    expires_in: int = Field(
        ..., description="URL expiration time in seconds (default 900 = 15 minutes)"
    )


class SessionResponse(SessionBase):
    id: uuid.UUID
    therapist_id: uuid.UUID
    processing_status: str
    job_id: Optional[str]
    s3_audio_key: Optional[str]
    session_duration_minutes: Optional[int]
    audio_metadata: Optional[Dict[str, Any]]
    summary: Optional[Dict[str, Any]]
    created_at: datetime.datetime
    processing_started_at: Optional[datetime.datetime]
    processing_completed_at: Optional[datetime.datetime]
    updated_at: datetime.datetime
    version: int

    class Config:
        from_attributes = True


class SessionFilter(BaseModel):

    patient_id: Optional[uuid.UUID] = Field(None, description="Filter by patient ID")
    processing_status: Optional[str] = Field(
        None,
        description="Filter by status (pending, processing, completed, failed, cancelled)",
    )
    session_date_from: Optional[datetime.datetime] = Field(
        None, description="Filter sessions from this date onwards"
    )
    session_date_to: Optional[datetime.datetime] = Field(
        None, description="Filter sessions up to this date"
    )


class PaginatedSessionResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    sessions: List[SessionResponse]


class SessionUpdate(BaseModel):
    processing_status: Optional[str] = Field(None, description="Update status")
    session_duration_minutes: Optional[int] = Field(None, description="Update duration")
    summary: Optional[Dict[str, Any]] = Field(None, description="Update summary")


class SessionSummary(BaseModel):
    main_points: List[str] = Field(default_factory=list)
    emotions_observed: List[Dict[str, str]] = Field(default_factory=list)
    behavioral_patterns: List[str] = Field(default_factory=list)
    action_items: List[Dict[str, str]] = Field(default_factory=list)
    risk_assessment: Dict[str, str] = Field(default_factory=dict)
    next_session_focus: List[str] = Field(default_factory=list)
    therapist_notes: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    tokens_used: Optional[Dict[str, int]] = None


class JobMessage(BaseModel):
    session_id: str
    therapist_id: str
    patient_id: str
    s3_key: str
    audio_metadata: Optional[Dict[str, Any]] = None
