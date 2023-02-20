from fastapi import APIRouter
from domain.utils.configs import refresh_configs
from domain.admin.admin import is_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)




@router.get("/refresh-configs/")
async def refresh_configs_fun():
    refresh_configs()


