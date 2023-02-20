## from http.client import HTTPException
from fastapi import APIRouter, Request
from domain.auth.main import login, activate_user, refresh, register_pending_user, resend_validation_code
from domain.auth.models import LoginRequest, RefreshRequest, RegisterPendingUserRequest, ActivateUserRequest, ResendCodeRequest
from db.base import engine
from api.models import StandardResponse
from domain.user.account import get_user_profile
from domain.customer import home as customer_home
from domain.user.models import UserProfile
from domain.utils.general import get_user_info

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_init_data(conn, role, user_id = None, user_profile: UserProfile = None):
    if role == "customer": return customer_home.get_init_data(conn, user_id)
    ## elif role == "manager": return manager_home.get_init_data(conn, user_id = user_id, user_profile = user_profile)


@router.post("/register/")
async def register_endpoint(request: Request, data: RegisterPendingUserRequest):
    with engine.begin() as conn:
        pending_user_id = register_pending_user(conn, "en", data)
        
        return StandardResponse.success_response(
            body = {
                "id": pending_user_id
            }
        )

@router.post("/token/")
async def login_endpoint(request: Request, data: LoginRequest):
    with engine.begin() as conn:
        user_profile, access_token, refresh_token = login(conn, request.state.current_user["lang"], data)

        return StandardResponse.success_response(
            body = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "init_data": get_init_data(conn, data.role, user_profile = user_profile)
            }
        )

@router.post("/refresh/")
async def refresh_endpoint(request: Request, data: RefreshRequest):
    with engine.begin() as conn:
        new_access_token = refresh(conn, data.role, request.state.current_user["lang"], data.refresh_token)

        return StandardResponse.success_response(
            body = {
                "access_token": new_access_token
            }
        )

@router.post("/activate-user/")
async def validate_user_func(request: Request, data: ActivateUserRequest):
    with engine.begin() as conn:
        access_token, refresh_token = activate_user(conn, request.state.current_user["lang"], data)
        user_profile = get_user_profile(conn, phone_number = data.phone_number, email = data.email)

        return StandardResponse.success_response(
            body = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "init_data": get_init_data(conn, data.role, user_profile = user_profile)
            }
        )


@router.post("/resend-code/")
async def resend_code_func(request: Request, data: ResendCodeRequest):
    with engine.begin() as conn:
        resend_validation_code(conn, request.state.current_user["lang"], data)
        return StandardResponse.success_response(body = {})





