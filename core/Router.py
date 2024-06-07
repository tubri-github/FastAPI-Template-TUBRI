# -*- coding:utf-8 -*-
"""
@Des: router aggreation
"""
from api.api import router
# from views.views import views_router
from fastapi import APIRouter


router = APIRouter()
# 视图路由
# router.include_router(views_router)
# API路由
router.include_router(router)