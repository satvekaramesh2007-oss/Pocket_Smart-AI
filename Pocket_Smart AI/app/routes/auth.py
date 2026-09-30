from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token
from app.services.auth_service import hash_password, verify_password, create_access_token, get_current_user, get_current_user_optional

router = APIRouter(tags=["Authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, response: Response, db: Session = Depends(get_db)):
    """Register a new user account with validated input and password hashing."""
    # Check duplicate email
    existing = db.query(User).filter(User.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Hash password securely
    hashed = hash_password(payload.password)
    new_user = User(
        name=payload.name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    token_str = create_access_token({"sub": str(new_user.id), "email": new_user.email})

    # Set HTTP-only Cookie
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_str}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserResponse.model_validate(new_user)
    )

@router.post("/login", response_model=Token)
def login_user(payload: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password credentials."
        )

    token_str = create_access_token({"sub": str(user.id), "email": user.email})

    response.set_cookie(
        key="access_token",
        value=f"Bearer {token_str}",
        httponly=True,
        max_age=86400,
        samesite="lax"
    )

    return Token(
        access_token=token_str,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.get("/logout")
def logout_user(response: Response):
    """Clear access token cookie and log user out."""
    response.delete_cookie("access_token")
    return {"message": "Successfully logged out."}

@router.get("/session-info")
def session_info(user: User = Depends(get_current_user)):
    """Return active user session details."""
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    }

@router.get("/session-data")
def session_data(user: Optional[User] = Depends(get_current_user_optional)):
    """Return optional session data without throwing 401 error."""
    if not user:
        return {"authenticated": False, "user": None}
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }
