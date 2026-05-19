from sqlalchemy import Column, ForeignKey, Integer, String, Table
from iris.database import Base

user_roles = Table( #記錄誰有什麼角色
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)


class Role(Base): #存四個角色名稱
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20), unique=True, nullable=False)