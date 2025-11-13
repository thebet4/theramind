from fastapi import APIRouter

from app.api.v1.v1_routes import router as v1_routes


router = APIRouter(prefix="/api")
router.include_router(v1_routes)
