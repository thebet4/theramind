from fastapi import Depends, HTTPException, Header
from jose import JWTError
from sqlalchemy.orm import Session
from app.core.auth import decode_token
from app.models.therapist import Therapist
from app.core.database import get_db
from app.schemas.therapist import TherapistResponse


def get_current_therapist(
    authorization: str = Header(...), db: Session = Depends(get_db)
) -> TherapistResponse:
    print(authorization)
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Expected 'Bearer <token>'",
        )

    token = authorization.replace("Bearer ", "", 1).strip()

    if not token:
        raise HTTPException(
            status_code=401, detail="Token missing in authorization header"
        )

    try:
        payload = decode_token(token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        therapist_id = payload.get("sub")
        if not therapist_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    therapist = db.query(Therapist).filter_by(id=therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")

    return TherapistResponse.model_validate(therapist)
