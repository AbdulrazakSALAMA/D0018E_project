import time
from typing import Union
import os

from fastapi import FastAPI, Request, HTTPException, Response, status
from pydantic import JsonError
from api.models import StandardResponse
from domain.admin.admin import is_admin
from domain.auth.security import validate_token_and_get_payload
from fastapi.responses import RedirectResponse, PlainTextResponse, JSONResponse
from domain.utils.configs import get_config
from domain.utils.general import DEPLOYMENT_VERSION, ENV
from domain.utils.enums import ConfigKey, MessageCode, Severity
from domain.utils.logging import log_message
from fastapi.responses import ORJSONResponse
import traceback

app = FastAPI(default_response_class=ORJSONResponse, version=DEPLOYMENT_VERSION)


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        content = StandardResponse.error_response(message = str(exc.detail), code = exc.status_code),
        status_code = 200
    )


# @app.on_event("startup")
# async def startup_event():
#     # do some initial stuff
#     pass


app.add_middleware(
        ValidateUploadFileMiddleware,
        app_path="/",
        max_size = get_config(ConfigKey.MAX_IMAGE_FILE_SIZE_MB) * 1024 * 1024,
        file_type=["text/plain"]
)

def is_protected_endpoint(url: str):
    # ToDo: check all protected endpoints
    protected_endpoint_prefixes = ["customer", "worker", "manager", "admin", "media", "user"]
    for prefix in protected_endpoint_prefixes:
        if url.startswith(f"/{prefix}/"): return True
    return False

def authenticate(request: Request):
    if not is_protected_endpoint(request.url.path): return { "id": None }
    if ENV == "dev": return {
        "id": request.headers.get("userid", "")
    }
    token = request.headers.get("Authorization", None)
    if not token: token = request.cookies.get("Authorization", None)
    return validate_token_and_get_payload(token)



@app.middleware("http")
async def middleware(request: Request, call_next):
    lang = request.headers.get("lang", "en")
    try:
        payload = authenticate(request)
    except Exception:
        return JSONResponse(
            content = {
                "success": False,
                "message": get_message(MessageCode.NOT_AUTHENTICATED, lang),
                "code": status.HTTP_401_UNAUTHORIZED
            },
            status_code = status.HTTP_200_OK
        )

    user_id = None
    if payload: user_id = payload.get("id", None)
    
    request.state.current_user = {
        "id": user_id,
        "lang": lang
    }

    if request.url.path.startswith("/admin/"):
        with engine.begin() as conn:
            if not is_admin(conn, user_id):
                return JSONResponse(
                    content = {
                        "success": False,
                        "message": get_message(MessageCode.NOT_FOUND, lang),
                        "code": status.HTTP_404_NOT_FOUND
                    },
                    status_code = status.HTTP_200_OK
                )
    
    try:
        return await call_next(request)
    except Exception as e:
        error_stack = traceback.format_exc()
        log_message(error_stack, severity = Severity.ERROR, code = 'internal-error')
        return JSONResponse(
            content = {
                "success": False,
                "message": error_stack if ENV in ["dev", "stg"] else get_message(MessageCode.INTERNAL_SERVER_ERROR, lang),
                "code": status.HTTP_500_INTERNAL_SERVER_ERROR
            },
            status_code = status.HTTP_200_OK
        )



# notice: when creating a new router file under /routers folder, add it here

from api.routers import public, test, auth, admin, manager, user, media, customer

app.include_router(test.router)
# app.include_router(test.router_extra)
app.include_router(auth.router)

app.include_router(admin.router)

app.include_router(manager.router)

app.include_router(user.router)

app.include_router(customer.router)

app.include_router(media.router)

app.include_router(public.router)


