from fastapi import APIRouter
from app.api.v1.therapist_routes import router as therapist_routes
from app.api.v1.auth_routes import router as auth_routes
from app.api.v1.patient_routes import router as patient_routes

router = APIRouter(prefix="/v1")

router.include_router(auth_routes)
router.include_router(therapist_routes)
router.include_router(patient_routes)
