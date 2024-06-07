# -*- coding:utf-8 -*-
"""
@Des: basic configuration
"""

import os
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings
from typing import List


class Config(BaseSettings):
    # load env varibles
    load_dotenv(find_dotenv(), override=True)
    # debug/prod
    APP_DEBUG: bool = True
    # project info
    VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Temp Fishnet2 API"
    DESCRIPTION: str = '<a href="/redoc" target="_blank">redoc</a>'
    # static resources path
    STATIC_DIR: str = os.path.join(os.getcwd(), "static")
    TEMPLATE_DIR: str = os.path.join(STATIC_DIR, "templates")
    # cors request
    CORS_ORIGINS: List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List = ["*"]
    CORS_ALLOW_HEADERS: List = ["*"]
    # Session
    SECRET_KEY: str = "session"
    SESSION_COOKIE: str = "session_id"
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60
    # Jwt
    # JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    # JWT_ALGORITHM = "HS256"
    # JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60
    #
    SWAGGER_UI_OAUTH2_REDIRECT_URL: str = "/api/v1/test/oath2"


settings = Config()