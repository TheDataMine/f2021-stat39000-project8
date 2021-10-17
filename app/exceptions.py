from fastapi import status, HTTPException
from pydantic import BaseModel
    

class APIException(HTTPException):
    """
    A wrapper around HTTPException that allows specifiying 
    defaults via class property.
    
    From https://github.com/tiangolo/fastapi/issues/1999
    """
    
    detail = None
    headers = None
    status_code = status.HTTP_400_BAD_REQUEST
    
    def __init__(self, *args, **kwargs):
        if "status_code" not in kwargs:
            kwargs["status_code"] = self.status_code
        if "detail" not in kwargs:
            kwargs["detail"] = self.detail
        if "headers" not in kwargs:
            kwargs["headers"] = self.headers
            
        super().__init__(*args, **kwargs)
        
    
    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}(status_code={self.status_code!r}, detail={self.detail!r})"
        

class NotFoundExceptionModel(BaseModel):
    message: str
    status_code: int = status.HTTP_404_NOT_FOUND
    type: str = "api_error"


class NotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found."
    headers = {"X-Error": "Resource not found"}
    type = "api_error"
    

class BadQueryParameterExceptionModel(BaseModel):
    message: str
    status_code: int = status.HTTP_404_NOT_FOUND
    type: str = "api_error"


class BadQueryParameterException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Bad query parameter."
    headers = {"X-Error": "Bad query parameter"}
    type = "api_error"


responses = {
    404: {"model": NotFoundExceptionModel, "description": f"{NotFoundException.detail}"},
    422: {"model": BadQueryParameterExceptionModel, "description": f"{BadQueryParameterException.detail}"},
}