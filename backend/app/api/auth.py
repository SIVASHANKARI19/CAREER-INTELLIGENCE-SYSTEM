from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import datetime
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, create_reset_token, decode_token
from app.models.user import User, UserRole
from app.models.student_profile import StudentProfile
from app.schemas.auth import (
    UserRegister, UserLogin, TokenResponse, RefreshTokenRequest,
    ForgotPasswordRequest, ResetPasswordRequest, UserOut
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UserOut)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    db_user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        role=user_in.role or UserRole.STUDENT,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Auto-create student profile if role is student
    if db_user.role == UserRole.STUDENT:
        profile = StudentProfile(
            user_id=db_user.id,
            full_name=user_in.full_name or user_in.email.split("@")[0].capitalize(),
            profile_completion_pct=25
        )
        db.add(profile)
        db.commit()

    return db_user

@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account is deactivated")

    user.last_login = datetime.datetime.utcnow()
    db.commit()

    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(body: RefreshTokenRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    new_access = create_access_token(data={"sub": str(user.id), "role": user.role})
    new_refresh = create_refresh_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=new_access, refresh_token=new_refresh)

@router.post("/forgot-password")
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        # Return success to prevent email enumeration
        return {"message": "Password reset instructions sent if email exists."}
    
    # NOTE: for demo purposes the token is returned directly since no SMTP/email
    # service is wired up yet. In production this must be emailed to the user,
    # never returned in the API response.
    reset_token = create_reset_token(data={"sub": str(user.id)})
    return {
        "message": "Password reset instructions sent if email exists.",
        "reset_token_mock": reset_token
    }

@router.post("/reset-password")
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    payload = decode_token(body.token)
    if payload.get("type") != "reset":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"message": "Password reset successfully."}

@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user