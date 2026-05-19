#定義register和login的資料格式：告訴 FastAPI 「register 要收什麼資料」和「要回傳什麼」。

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8)


#加上role欄位，讓response能顯示user有哪些角色
class RoleResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    roles: list[RoleResponse] = []

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str

class ForgotPasswordRequest(BaseModel):
    username: str


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(min_length=8)