#把users的crud， schemas 和core的security都引進來，實作註冊和登入的路由

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from iris.database import get_db
from iris.config import settings
from app.users import crud
from app.users.schemas import RegisterRequest, UserResponse, LoginRequest
from app.core.security import verify_password, create_access_token
from app.core.tokens import create_refresh_token, verify_refresh_token, revoke_refresh_token, revoke_all_refresh_tokens
from app.core.deps import get_current_user
from app.core.ratelimit import check_login_locked, record_login_failure, clear_login_failures, check_ip_rate_limit
from app.audit.service import write_audit
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if crud.get_by_username(db, body.username):
        raise HTTPException(status_code=400, detail="Username already taken")
    if crud.get_by_email(db, body.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    user = crud.create_user(db, body.username, body.email, body.password)
    write_audit(db, action="user_created", result="ok", actor_user_id=user.id, resource_type="user", resource_id=str(user.id))
    return user


@router.post("/login")
async def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    ip = request.client.host
    if await check_ip_rate_limit(ip):
        raise HTTPException(status_code=429, detail="Too many requests")
    if await check_login_locked(body.username):
        raise HTTPException(status_code=429, detail="Account temporarily locked")
    user = crud.get_by_username(db, body.username)
    if not user or not verify_password(body.password, user.password_hash):
        await record_login_failure(body.username)
        write_audit(db, action="login_failure", result="fail", ip_address=ip, extra={"username": body.username})
        raise HTTPException(status_code=401, detail="Invalid credentials")
    await clear_login_failures(body.username)
    access = create_access_token(user.id)
    refresh = await create_refresh_token(user.id)
    write_audit(db, action="login_success", result="ok", actor_user_id=user.id, ip_address=ip)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_minutes * 60,
    }


@router.post("/refresh")
async def refresh(body: dict, db: Session = Depends(get_db)):
    token = body.get("refresh_token")
    if not token:
        raise HTTPException(status_code=400, detail="refresh_token required")
    user_id = await verify_refresh_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")
    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token")
    await revoke_refresh_token(token)
    access = create_access_token(user.id)
    new_refresh = await create_refresh_token(user.id)
    return {
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": settings.access_token_ttl_minutes * 60,
    }


@router.post("/logout")
async def logout(body: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = body.get("refresh_token")
    if token:
        await revoke_refresh_token(token)
    write_audit(db, action="logout", result="ok", actor_user_id=current_user.id)
    return {"status": "logged out"}


@router.post("/logout-all")
async def logout_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    await revoke_all_refresh_tokens(current_user.id)
    write_audit(db, action="logout_all", result="ok", actor_user_id=current_user.id)
    return {"status": "all sessions revoked"}


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user