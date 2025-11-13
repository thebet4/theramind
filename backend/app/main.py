from fastapi import FastAPI

from app.api.api_routes import router as api_routes

from app.models import Therapist, Patient, Session, AuditLog, ProcessingError

app = FastAPI()

app.include_router(api_routes)
