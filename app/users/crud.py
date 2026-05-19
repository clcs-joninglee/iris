#負責跟 DB 溝通，兩個功能：
#用 username 或 email 查找 user（login 時用）
#建立新 user（register 時用）

from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import hash_password


def get_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password: str) -> User:
    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user