from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from src.application.common.exceptions import ConflictError
from src.application.common.exceptions import NotFoundError
from src.domain.exceptions import DomainError
from src.domain.exceptions import InvalidTaskStatusError


def _error(detail: str) -> dict[str, str]:
    return {"detail": detail}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content=_error(str(exc)))

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content=_error(str(exc)))

    @app.exception_handler(InvalidTaskStatusError)
    async def invalid_status_handler(request: Request, exc: InvalidTaskStatusError) -> JSONResponse:
        return JSONResponse(status_code=422, content=_error(str(exc)))

    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=422, content=_error(str(exc)))

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        return JSONResponse(status_code=409, content=_error("Resource already exists"))

    @app.exception_handler(ValidationError)
    async def pydantic_validation_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
