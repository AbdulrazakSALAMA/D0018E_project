from typing import Optional
from fastapi import APIRouter, Request, status
from domain.customer import home, models

from domain.utils.general import get_user_info

from db.base import engine
from time import sleep
## from api.models import StandardResponse


router = APIRouter(
    prefix="/customer",
    tags=["customer"],
)

@router.get("/init/", response_model = Optional[models.CustomerInitData])
async def init_endpoint(request: Request):
    with engine.begin() as conn:
        return home.get_init_data(conn, get_user_info(request).id)

