# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

from hagworm.frame.fastapi.base import APIRouter

from controller import home


router = APIRouter(prefix=r'/demo')

router.include_router(home.router)
