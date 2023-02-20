
from pydantic import BaseModel


class RegisterPendingUserRequest(BaseModel):
    email: str = None
    phone_number: str = None
    password: str
    role: str = "customer"
    name: str = None


class LoginRequest(BaseModel):
    email: str = None
    phone_number: str = None
    password: str
    role: str = "customer"

    
class RefreshRequest(BaseModel):
    refresh_token: str
    role: str = "customer"


class ActivateUserRequest(BaseModel):
    pending_user_id: int
    role: str
    email: str = None
    phone_number: str = None
    validation_code: int


class ResendCodeRequest(BaseModel):
    email: str = None
    phone_number: str = None
    pending_user_id: int



