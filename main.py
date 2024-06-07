# -*- coding:utf-8 -*-
"""
@Des: app main entre
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from h11 import Request
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from fastapi.staticfiles import StaticFiles
from core import Exception, Router, Events, Middleware
from fastapi.templating import Jinja2Templates
# from tortoise.exceptions import OperationalError, DoesNotExist, IntegrityError, ValidationError
from fastapi.openapi.docs import (get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html)
from fastapi.openapi.utils import get_openapi
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from pydantic import BaseModel




app = FastAPI(
    debug=settings.APP_DEBUG,
    version='1.0.0',
    docs_url=None,
    redoc_url=None,
    swagger_ui_oauth2_redirect_url=settings.SWAGGER_UI_OAUTH2_REDIRECT_URL,
)

class SearchParams(BaseModel):
    vtaxon: Optional[str] = None
    vlocation: Optional[str] = None
    vcatalognumber: Optional[str] = None
    vdaterange: Optional[str] = None
    vother: Optional[str] = None
    vpoly: Optional[str] = None
    vmap: Optional[str] = None
    vstrict: bool = False
    vstartrl: Optional[int] = None
    vrlcount: Optional[int] = None
    vcols: Optional[str] = None
    voutputtype: bool = False
    vdebug: bool = False

# custom_openapi
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        title=settings.PROJECT_NAME,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# custom_swagger_ui_html
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url
    )


# swagger_ui_oauth2_redirect_url
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# redoc
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/standalone.js",
    )


# event listener
app.add_event_handler("startup", Events.startup(app))
app.add_event_handler("shutdown", Events.stopping(app))

# exception handle
app.add_exception_handler(HTTPException, Exception.http_error_handler)
app.add_exception_handler(RequestValidationError, Exception.http422_error_handler)
app.add_exception_handler(Exception.UnicornException, Exception.unicorn_exception_handler)
# application.add_exception_handler(DoesNotExist, Exception.mysql_does_not_exist)
# application.add_exception_handler(IntegrityError, Exception.mysql_integrity_error)
# application.add_exception_handler(ValidationError, Exception.mysql_validation_error)
# application.add_exception_handler(OperationalError, Exception.mysql_operational_error)


# middle ware
app.add_middleware(Middleware.BaseMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie=settings.SESSION_COOKIE,
    max_age=settings.SESSION_MAX_AGE
)
from api.api import router as api_router
# router
app.include_router(api_router)

# static folder path
app.mount('/', StaticFiles(directory=settings.STATIC_DIR), name="static")


# application.state.views = Jinja2Templates(directory=settings.TEMPLATE_DIR)


@app.get('/')
async def home():
    return "fastapi"

@app.get("/taxa/", tags=["Taxa"])
# async def read_multimedias(response: Response, genus: Optional[str] = None, dataset: schemas.DatasetName = schemas.DatasetName.glindataset, min_height: Optional[int] = None, max_height: Optional[int] = None, limit: Optional[int] = None, zipfile: bool = True,
async def getTaxa():
    '''
        PUBLIC METHOD
        A demo for getting multimedias and associated (meta)data, like IQ, extended metadata, hirecachy medias
        - param genus: species genus
        - param family: species family
        - param institution: institution code
        - param dataset: dataset name(multiple selection)
        - param maxWidth: max width of image
        - param minWidth: min width of image
        - param maxHeight: max height of image
        - param minHeight: min height of image
        - param batchARKID: batch ARK ID
        - param zipfile: return JSON or Zip file
        - return: a list of 200 multimedias (with associated (meta)data). If zipfile is false, it will return 20 records
    '''

    return None

@app.get("/providers/", tags=["Providers"])
# async def read_multimedias(response: Response, genus: Optional[str] = None, dataset: schemas.DatasetName = schemas.DatasetName.glindataset, min_height: Optional[int] = None, max_height: Optional[int] = None, limit: Optional[int] = None, zipfile: bool = True,
async def read_providers():
    '''
        PUBLIC METHOD
        A demo for getting multimedias and associated (meta)data, like IQ, extended metadata, hirecachy medias
        - param genus: species genus
        - param family: species family
        - param institution: institution code
        - param dataset: dataset name(multiple selection)
        - param maxWidth: max width of image
        - param minWidth: min width of image
        - param maxHeight: max height of image
        - param minHeight: min height of image
        - param batchARKID: batch ARK ID
        - param zipfile: return JSON or Zip file
        - return: a list of 200 multimedias (with associated (meta)data). If zipfile is false, it will return 20 records
    '''

    return None

@app.get("/occurrenceCount/", tags=["Occurrence"])
# async def read_multimedias(response: Response, genus: Optional[str] = None, dataset: schemas.DatasetName = schemas.DatasetName.glindataset, min_height: Optional[int] = None, max_height: Optional[int] = None, limit: Optional[int] = None, zipfile: bool = True,
async def read_multimedias():
    '''
        PUBLIC METHOD
        A demo for getting multimedias and associated (meta)data, like IQ, extended metadata, hirecachy medias
        - param genus: species genus
        - param family: species family
        - param institution: institution code
        - param dataset: dataset name(multiple selection)
        - param maxWidth: max width of image
        - param minWidth: min width of image
        - param maxHeight: max height of image
        - param minHeight: min height of image
        - param batchARKID: batch ARK ID
        - param zipfile: return JSON or Zip file
        - return: a list of 200 multimedias (with associated (meta)data). If zipfile is false, it will return 20 records
    '''

    return None

@app.get("/avaliablemaps/", tags=["Maps"])
# async def read_multimedias(response: Response, genus: Optional[str] = None, dataset: schemas.DatasetName = schemas.DatasetName.glindataset, min_height: Optional[int] = None, max_height: Optional[int] = None, limit: Optional[int] = None, zipfile: bool = True,
async def read_multimedias():
    '''
        PUBLIC METHOD
        A demo for getting multimedias and associated (meta)data, like IQ, extended metadata, hirecachy medias
        - param genus: species genus
        - param family: species family
        - param institution: institution code
        - param dataset: dataset name(multiple selection)
        - param maxWidth: max width of image
        - param minWidth: min width of image
        - param maxHeight: max height of image
        - param minHeight: min height of image
        - param batchARKID: batch ARK ID
        - param zipfile: return JSON or Zip file
        - return: a list of 200 multimedias (with associated (meta)data). If zipfile is false, it will return 20 records
    '''

    return None

@app.get("/location/", tags=["Locations"])
# async def read_multimedias(response: Response, genus: Optional[str] = None, dataset: schemas.DatasetName = schemas.DatasetName.glindataset, min_height: Optional[int] = None, max_height: Optional[int] = None, limit: Optional[int] = None, zipfile: bool = True,
async def read_multimedias():
    '''
        PUBLIC METHOD
        A demo for getting multimedias and associated (meta)data, like IQ, extended metadata, hirecachy medias
        - param genus: species genus
        - param family: species family
        - param institution: institution code
        - param dataset: dataset name(multiple selection)
        - param maxWidth: max width of image
        - param minWidth: min width of image
        - param maxHeight: max height of image
        - param minHeight: min height of image
        - param batchARKID: batch ARK ID
        - param zipfile: return JSON or Zip file
        - return: a list of 200 multimedias (with associated (meta)data). If zipfile is false, it will return 20 records
    '''

    return None
