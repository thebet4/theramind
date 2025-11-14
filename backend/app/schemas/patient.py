import datetime
from typing import Optional, List
import uuid
from pydantic import BaseModel, Field


class PatientBase(BaseModel):
    identifier: str
    date_of_birth: Optional[datetime.datetime]


class PatientResponse(PatientBase):
    id: uuid.UUID
    consent_given: bool
    created_at: datetime.datetime

    class Config:
        from_attributes = True


class PatientCreate(BaseModel):
    identifier: str
    date_of_birth: Optional[datetime.datetime]


class PatientFilter(BaseModel):
    identifier: Optional[str] = Field(
        None, description="Search by patient identifier (partial match)"
    )
    consent_given: Optional[bool] = Field(None, description="Filter by consent status")
    created_after: Optional[datetime.datetime] = Field(
        None, description="Filter patients created after this date"
    )
    created_before: Optional[datetime.datetime] = Field(
        None, description="Filter patients created before this date"
    )


class PaginatedPatientResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    patients: List[PatientResponse]


class PatientUpdate(BaseModel):
    identifier: Optional[str] = Field(None, description="Update patient identifier")
    date_of_birth: Optional[datetime.datetime] = Field(
        None, description="Update patient date of birth"
    )
