from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.models import PatientProfile, User
from app.schemas.schemas import TokenOut, UserLogin, UserRegister

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenOut)
def register(body: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(400, "An account with this email already exists")

    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        role=body.role,
        created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if user.role == "patient":
        db.add(PatientProfile(user_id=user.id, medical_record_number=f"MRN-{100000 + user.id}"))
        db.commit()

    token = create_access_token(subject=user.email, role=user.role)
    return TokenOut(access_token=token, user=user)


@router.post("/login", response_model=TokenOut)
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(401, "Incorrect email or password")

    token = create_access_token(subject=user.email, role=user.role)
    return TokenOut(access_token=token, user=user)
