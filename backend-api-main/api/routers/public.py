
import os
from fastapi import APIRouter, Request
from db.base import engine


router = APIRouter(
    prefix="/public",
    tags=["public"],
)


@router.post("/configs/")
async def app_configs(request: Request):
    return {
        "allowed_country_codes": os.getenv("ALLOWED_COUNTRY_CODES", "46").split(",")
    }
        

