from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from iris.database import get_db
from app.core.deps import get_current_user, require_role
from app.models.user import User
from app.models.role import Role
from app.users.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("", response_model=list[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    return db.query(User).all()


@router.patch("/{user_id}/roles", response_model=UserResponse)
def update_roles(
    user_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: User = Depends(require_role("admin")),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    role_names = body.get("roles", [])
    roles = db.query(Role).filter(Role.name.in_(role_names)).all()
    user.roles = roles
    db.commit()
    db.refresh(user)
    return user