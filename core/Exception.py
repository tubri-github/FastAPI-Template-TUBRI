# -*- coding:utf-8 -*-
"""
@Des: exception handler
"""

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from typing import Union
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from enum import Enum


class ErrorCodes(Enum):
    INV_PolyFormat = "invalid polygon format"
    INV_MinTerms = "at least one term required"
    INV_DateRangeFromat = "invalid date range"
    INV_MapName = "invalid map name"
    INV_PolygonWKT = "Polygon is not validly formatted WKT"


async def http_error_handler(_: Request, exc: HTTPException):
    """
    http exceptions
    :param _:
    :param exc:
    :return:
    """
    if exc.status_code == 401:
        return JSONResponse({exc.detail}, status_code=exc.status_code)

    return JSONResponse({
        exc.detail
    }, status_code=exc.status_code, headers=exc.headers)


class UnicornException(Exception):

    def __init__(self, code, errmsg, data=None):
        """
        failure return format
        :param code:
        :param errmsg:
        """
        if data is None:
            data = {}
        self.code = code
        self.errmsg = errmsg
        self.data = data


async def unicorn_exception_handler(_: Request, exc: UnicornException):
    """
    unicorn exceptions
    :param _:
    :param exc:
    :return:
    """
    return JSONResponse({
        "code": exc.code,
        "message": exc.errmsg,
        "data": exc.data,
    })


async def http422_error_handler(_: Request, exc: Union[RequestValidationError, ValidationError], ) -> JSONResponse:
    """
    parameters validation
    :param _:
    :param exc:
    :return:
    """
    print("[422]", exc.errors())
    return JSONResponse(
        {
            "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "message": f"data validation error {exc.errors()}",
            "data": exc.errors(),
        },
        status_code=422,
    )


class ValidationError(Exception):
    def __init__(self, code: ErrorCodes):
        self.code = code


async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=200,
        content={"error": exc.code.value},
    )


async def sql_exception_handler(_: Request, exc: SQLAlchemyError):
    if "Polygon is not validly formatted WKT" in str(exc):
        return JSONResponse(
            status_code=200,
            content={ErrorCodes.INV_PolygonWKT.value},
        )
    return JSONResponse(
        status_code=200,
        content={"A database error occurred." + str(exc)},
    )


async def global_exception_handler(_: Request, exc: Exception):

    return JSONResponse(
        status_code=200,
        content= {str(exc)}
    )
