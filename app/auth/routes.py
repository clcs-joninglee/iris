#把users的crud， schemas 和core的security都引進來，實作註冊和登入的路由

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from iris.database import get_db
from iris.config import settings
from app.users import crud
from app.users.schemas import RegisterRequest, UserResponse, LoginRequest
from app.core.security import verify_password, create_access_token, generate_totp_secret, get_totp_uri, verify_totp
from app.core.tokens import create_refresh_token, verify_refresh_token, revoke_refresh_token, revoke_all_refresh_tokens
from app.core.deps import get_current_user
from app.core.ratelimit import check_login_locked, record_login_failure, clear_login_failures, check_ip_rate_limit
from app.audit.service import write_audit
from app.models.user import User

from app.core.tokens import create_reset_token, verify_reset_token, consume_reset_token
from app.core.security import hash_password

from app.users.schemas import RegisterRequest, UserResponse, LoginRequest, ForgotPasswordRequest, ResetPasswordRequest  

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
    if user.totp_enabled:
        return {"totp_required": True, "user_id": user.id}
    access = create_access_token(user.id)
    refresh = await create_refresh_token(user.id)
    write_audit(db, action="login_success", result="ok", actor_user_id=user.id, ip_address=ip)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "expires_in": settings.access_token_ttl_minutes * 60}


@router.post("/totp/setup")
def totp_setup(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = generate_totp_secret()
    current_user.totp_secret = secret
    db.commit()
    return {"uri": get_totp_uri(secret, current_user.username)}


@router.post("/totp/verify")
def totp_verify(body: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    code = body.get("code", "")
    if not current_user.totp_secret or not verify_totp(current_user.totp_secret, code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    current_user.totp_enabled = True
    db.commit()
    return {"status": "2FA enabled"}


@router.post("/totp/login")
async def totp_login(body: dict, db: Session = Depends(get_db)):
    user_id = body.get("user_id")
    code = body.get("code", "")
    user = db.get(User, user_id)
    if not user or not user.totp_enabled or not user.totp_secret:
        raise HTTPException(status_code=401, detail="Invalid request")
    if not verify_totp(user.totp_secret, code):
        raise HTTPException(status_code=401, detail="Invalid TOTP code")
    access = create_access_token(user.id)
    refresh = await create_refresh_token(user.id)
    write_audit(db, action="login_success", result="ok", actor_user_id=user.id)
    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer", "expires_in": settings.access_token_ttl_minutes * 60}


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
    return {"access_token": access, "refresh_token": new_refresh, "token_type": "bearer", "expires_in": settings.access_token_ttl_minutes * 60}


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

@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = crud.get_by_username(db, body.username)
    if not user:
        return {"reset_token": None, "detail": "If the account exists, a token has been issued"}
    token = await create_reset_token(user.id)
    return {"reset_token": token}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    user_id = await verify_reset_token(body.reset_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired reset token")
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    await consume_reset_token(body.reset_token)
    await revoke_all_refresh_tokens(user_id)
    write_audit(db, action="password_reset", result="ok", actor_user_id=user_id)
    return {"status": "password reset successful"}