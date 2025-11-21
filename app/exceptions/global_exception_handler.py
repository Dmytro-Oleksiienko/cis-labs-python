from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError


class NotFoundException(Exception):
    def __init__(self, message: str):
        self.message = message


def register_exception_handlers(app):

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "NOT_FOUND",
                "message": exc.message
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "BAD_REQUEST",
                "message": str(exc)
            }
        )

    @app.exception_handler(IntegrityError)
    async def db_integrity_handler(request: Request, exc: IntegrityError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={
                "error": "DATA_INTEGRITY_VIOLATION",
                "message": "DB constraint violated (value too long, null, or FK issue)"
            }
        )