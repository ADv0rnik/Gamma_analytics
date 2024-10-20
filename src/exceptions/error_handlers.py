from fastapi.exceptions import RequestValidationError
from fastapi import Request, status
from fastapi.responses import JSONResponse

from .error_codes import ErrorCodesEnum


class BaseCustomException(Exception):
    def __init__(self, error_code):
        super().__init__(error_code)
        self.error_code = error_code


class WrongFileFormatException(BaseCustomException):
    pass


async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "errCode": ErrorCodesEnum.INTERNAL_SERVER_ERROR.value,
            "message": f"An unexpected error occurred. {type(exc).__name__}"
        }
    )


async def wrong_file_format_exception_handler(
        request: Request, exc: WrongFileFormatException
):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error_code": exc.error_code,
            "message": "Wrong file format or file is not received"
        }
    )
