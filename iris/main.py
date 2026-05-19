from contextlib import asynccontextmanager
from typing import AsyncGenerator

import app
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from iris.routes.iris import router as iris_router
from app.auth.routes import router as auth_router
from app.users.routes import router as users_router
from app.audit.routes import router as audit_router

from fastapi.security import HTTPBearer


@asynccontextmanager #在db裏創立四個角色，app啟動的時候會自動執行這段程式碼
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    from iris.database import SessionLocal
    from app.models.role import Role
    db = SessionLocal()
    try:
        for name in ("admin", "scientist", "viewer", "readonly"):
            if not db.query(Role).filter(Role.name == name).first():
                db.add(Role(name=name))
        db.commit()
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Iris API",
        description="Iris dataset CRUD + analytics API",
        version="0.1.0",
        lifespan=lifespan,
        swagger_ui_parameters={"persistAuthorization": True}
    )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=500,
            content={"detail": "A database error occurred."},
        )

    @app.exception_handler(Exception)
    async def generic_error_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred."},
        )

    app.include_router(iris_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(audit_router)
    return app


app = create_app()