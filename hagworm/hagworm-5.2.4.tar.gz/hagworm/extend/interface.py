# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import traceback

from .base import Utils
from .error import Ignore


class FunctorInterface:
    """仿函数接口定义
    """

    def __call__(self):
        raise NotImplementedError()


class RunnableInterface:
    """Runnable接口定义
    """

    def run(self):
        raise NotImplementedError()


class TaskInterface:
    """Task接口定义
    """

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()

    def is_running(self):
        raise NotImplementedError()


class ObjectFactoryInterface:
    """对象工厂类接口定义
    """

    def create(self):
        raise NotImplementedError()


class ContextManager:
    """上下文资源管理器

    子类通过实现_context_release接口，方便的实现with语句管理上下文资源释放

    """

    def __enter__(self):

        self._context_initialize()

        return self

    def __exit__(self, exc_type, exc_value, _traceback):

        self._context_release()

        if exc_type and issubclass(exc_type, Ignore):

            return not exc_value.throw()

        elif exc_value:

            Utils.log.error(traceback.format_exc())

            return True

    def _context_initialize(self):

        pass

    def _context_release(self):

        raise NotImplementedError()


class AsyncContextManager:
    """异步上下文资源管理器

    子类通过实现_context_release接口，方便的实现with语句管理上下文资源释放

    """

    async def __aenter__(self):

        await self._context_initialize()

        return self

    async def __aexit__(self, exc_type, exc_value, _traceback):

        await self._context_release()

        if exc_type and issubclass(exc_type, Ignore):

            return not exc_value.throw()

        elif exc_value:

            Utils.log.error(traceback.format_exc())

            return True

    async def _context_initialize(self):

        pass

    async def _context_release(self):

        raise NotImplementedError()
