from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from .exceptions import *

async def not_found_exception_handler(request: Request, exception: NotFoundException):
    return JSONResponse(
        status_code=exception.status_code,
        content={"message": exception.detail, "type": exception.type, "status_code": exception.status_code}
    )
    

async def bad_query_parameter_exception_handler(request: Request, exception: BadQueryParameterException):
    return JSONResponse(
        status_code=exception.status_code,
        content={"message": exception.detail, "type": exception.type, "status_code": exception.status_code}
    )