from fastapi import APIRouter, Request
from db.base import engine
from api.models import StandardResponse
from domain.user.account import get_user_profile
from domain.utils.general import get_user_info


router = APIRouter(
    prefix="/user",
    tags=["user"],
)


@router.get("/profile/details/")
async def profile_details_func(request: Request):
    with engine.begin() as conn:
        return StandardResponse.success_response(
            body = get_user_profile(conn, user_info = get_user_info(request))
        )

