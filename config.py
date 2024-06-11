# -*- coding:utf-8 -*-
"""
@Des: basic configuration
"""

import os
from dotenv import load_dotenv, find_dotenv
from pydantic_settings import BaseSettings
from typing import List


class Config(BaseSettings):
    # load environment variables .env file
    load_dotenv(find_dotenv(), override=True)

    # debug/prod
    APP_DEBUG: bool = os.getenv('APP_DEBUG', 'true').lower() in ['true', '1', 't']

    # project info
    VERSION: str = "1.0.0"
    PROJECT_NAME: str = "Temp Fishnet2 API"
    DESCRIPTION: str = '<a href="/redoc" target="_blank">redoc</a>'

    # static resources path
    STATIC_DIR: str = os.path.join(os.getcwd(), "static")
    TEMPLATE_DIR: str = os.path.join(STATIC_DIR, "templates")

    # cors request
    CORS_ORIGINS: List[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Session
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'session')
    SESSION_COOKIE: str = "session_id"
    SESSION_MAX_AGE: int = 14 * 24 * 60 * 60

    # Jwt
    # JWT_SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    # JWT_ALGORITHM = "HS256"
    # JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60

    # Swagger
    SWAGGER_UI_OAUTH2_REDIRECT_URL: str = "/api/v1/test/oath2"

    # Database URLs
    DATABASE_URL_LOCAL: str = os.getenv('DATABASE_URL_LOCAL')
    DATABASE_URL_REMOTE: str = os.getenv('DATABASE_URL_REMOTE')
    USE_LOCAL_DB: bool = os.getenv('USE_LOCAL_DB', 'true').lower() in ['true', '1', 't']

    @property
    def DATABASE_URL(self):
        return self.DATABASE_URL_LOCAL if self.USE_LOCAL_DB else self.DATABASE_URL_REMOTE


settings = Config()
