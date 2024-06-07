# -*- coding:utf-8 -*-
"""

@Des: fastapi event listener
"""

from typing import Callable
from fastapi import FastAPI
# from database.mysql import register_mysql
# from database.redis import sys_cache, code_cache
# from aioredis import Redis


def startup(app: FastAPI) -> Callable:
    """
    FastApi startup event
    :param app: FastAPI
    :return: start_app
    """
    async def app_start() -> None:
        print("fastapi has started up")
        # db register
        # await register_mysql(app)
        # # inject cache to app
        # app.state.cache = await sys_cache()
        # app.state.code_cache = await code_cache()

        pass
    return app_start


def stopping(app: FastAPI) -> Callable:
    """
    FastApi stop event
    :param app: FastAPI
    :return: stop_app
    """
    async def stop_app() -> None:
        print("fastapi has stopped")
        # cache: Redis = await app.state.cache
        # code: Redis = await app.state.code_cache
        # await cache.close()
        # await code.close()

    return stop_app