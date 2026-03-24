from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import create_access_token, hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthService:
    CUSTOMER_ROLE = "customer"

    def __init__(self, db: Session) -> None:
        self.db = db

    def register_user(self, payload: RegisterRequest) -> User:
        existing_user = self.db.query(User).filter(User.email == payload.email).first()
        if existing_user is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered",
            )

        customer_role = self.db.query(Role).filter(Role.name == self.CUSTOMER_ROLE).first()
        if customer_role is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default customer role is not configured",
            )

        user = User(
            role_id=customer_role.id,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            hashed_password=hash_password(payload.password),
            is_active=True,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        user = (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.id == user.id)
            .first()
        )
        return user

    def authenticate_user(self, payload: LoginRequest) -> User:
        user = (
            self.db.query(User)
            .options(joinedload(User.role))
            .filter(User.email == payload.email)
            .first()
        )
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive",
            )
        return user

    def build_auth_response(self, user: User) -> dict:
        return {
            "access_token": create_access_token(user_id=user.id, role=user.role.name),
            "token_type": "bearer",
            "user": user,
        }
