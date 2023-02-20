
from typing import Any
from fastapi import Response
from pydantic import BaseModel, Json
from fastapi.encoders import jsonable_encoder





class StandardResponse(BaseModel):
    success: bool = True
    result: Any
    message: str = None
    code: int = 200

    @classmethod
    def success_response(self, body):
        result = StandardResponse(
            result = body
        )
        return jsonable_encoder(result)

    @classmethod
    def error_response(self, message: str, code: int = 0):
        result = StandardResponse(
            success = False,
            result = None,
            message = message,
            code = code
        )
        return jsonable_encoder(result)



