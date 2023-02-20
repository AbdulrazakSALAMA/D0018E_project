from fastapi import APIRouter, Request, status
from domain.manager import models
from domain.user.account import get_user_profile
from domain.utils.enums import ManagerCompanyPermission
from domain.utils.general import get_user_info
from db.base import engine
 ##from api.models import StandardResponse


PAGE_SIZE = 20

router = APIRouter(
    prefix="/manager",
    tags=["manager"],
)

