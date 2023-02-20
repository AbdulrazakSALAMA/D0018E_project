from pydantic import BaseModel
from typing import List


class Owner(BaseModel):
    user_id: int
    name: str = None

class ManagerPermissions(BaseModel):
    company_permissions: List[str] = None

class ManagerInviteSendRequest(BaseModel):
    qr_code: bool = False
    invited_manager_id: int = None
    permissions: ManagerPermissions

class ManagerInviteSendResponse(BaseModel):
    verification_code: int = None
    manager_invite_id: int

