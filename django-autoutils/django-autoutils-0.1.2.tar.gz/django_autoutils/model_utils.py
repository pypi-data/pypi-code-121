"""
    All utils for model
"""
import hashlib
import logging
import os
import random
import string
from threading import Thread
from typing import Callable

from django.contrib.auth import get_user_model
from django.contrib.messages import add_message
from django.db import models, transaction, IntegrityError, OperationalError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from django_autoutils.exceptions import RequestException
from django_autoutils.utils import get_request_obj

logger = logging.getLogger("django_autoutils")


def model_transaction(nowait=False, thread=False):
    """
        Use this decorator for run input function in transaction
    """

    def inner(func: Callable):
        """
            Class decorator for run in transaction
        """

        def wrapper(obj, request, *args, **kwargs):
            """
                Wrapper function for handle extra functions before main function
            Args:
                obj (AbstractModel):
                request: django request
                *args: extra data
                **kwargs: extra data
            """
            if obj.is_in_updating(nowait=nowait):
                obj.message_log(request, logging.ERROR, f"last progress not finished yet")
                return
            try:
                with transaction.atomic():
                    new_obj = obj.select_for_update()
                    if thread:
                        j = Thread(target=func, args=(new_obj, request, *args), kwargs=kwargs)
                        j.start()
                        obj.message_log(request, logging.INFO, f"job will run in background")
                    else:
                        return func(new_obj, request, *args, **kwargs)
            except IntegrityError:
                obj.message_log(request, logging.ERROR, f"error run in transaction function {func.__name__}")

        return wrapper

    return inner


def view_transaction(get_object: "Callable" = None, nowait=False):
    """
        Use this decorator for update user related
    """

    def inner(func: "Callable"):
        """
            Class decorator for run in transaction
        """

        def wrapper(view, request, *args, **kwargs):
            """
                Wrapper function for handle extra functions before main function
            Args:
                view: view object
                request: django request
                *args: extra data
                **kwargs: extra data
            """
            if callable(get_object):
                update_object = get_object(view, request)
            else:
                update_object = request.user
                user_model = get_user_model()
                if not isinstance(update_object, user_model):
                    raise exceptions.AuthenticationFailed("can not find user")
            if update_object.is_in_updating(nowait=nowait):
                update_object.message_log(request, logging.ERROR, f"last progress not finished yet")
                raise RequestException(request)
            try:
                with transaction.atomic():
                    new_update_object = update_object.select_for_update()
                    return func(view, request, new_update_object, *args, **kwargs)
            except IntegrityError as e:
                update_object.message_log(request, logging.ERROR, f"error run in transaction function {func.__name__}")
                update_object.log(logging.ERROR, f"error run in transaction function {func.__name__}. error: {e}")
                raise RequestException(request)

        return wrapper

    return inner


def upload_file(instance, filename=None) -> str:
    """
        Upload user image

    Returns:
        (str) : path of file
    """
    filename, file_extension = os.path.splitext(filename)
    random_char = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(96))
    hash_date = hashlib.md5(str(timezone.now().timestamp()).encode()).hexdigest()
    path = os.path.join(f"{instance.__class__.__name__}", f"{random_char}{hash_date}{file_extension}")
    return path


class AbstractModel(models.Model):
    """
        All models must be extend this model
    """
    BASE_PERMISSION_OBJECT = None
    insert_dt = models.DateTimeField(_("insert time"), auto_now_add=True)
    update_dt = models.DateTimeField(_("update time"), auto_now=True)

    class Meta:
        abstract = True

    def _get_message(self, message):
        return f"'{self}': {message}"

    def _set_log_data(self, data: dict):
        pass

    def log(self, level: int, message: str, data: dict = None):
        """
            Use for all logs
        """
        if data is None:
            data = {}
        if logger.isEnabledFor(level):
            self._set_log_data(data)
            # noinspection PyProtectedMember
            logger._log(level, self._get_message(message), (data,))

    def message_log(self, request, level: int, message: str, data: dict = None):
        """
            For message log
        """
        if request is None:
            request = get_request_obj()
        if request is not None:
            add_message(request, level, self._get_message(message))
        self.log(level=level, message=message, data=data)

    def get_obj(self):
        """
            Get object for permission
        """
        if self.id is None:
            return None
        return self._get_obj()

    def _get_obj(self):
        if self.BASE_PERMISSION_OBJECT is None:
            return self
        base_object = getattr(self, self.BASE_PERMISSION_OBJECT, None)
        if base_object is None:
            return None
        return base_object.get_obj()

    def select_for_update(self, nowait=False):
        """
            Check last state is in running

            Returns:
                (bool) : for select for update an object.
        """
        try:
            return self.queryset().select_for_update(nowait=nowait).get()
        except OperationalError:
            return None

    def is_in_updating(self, nowait=True):
        """
            Check last state is in running

            Returns:
                (bool) : true for if it is in updating
        """
        try:
            with transaction.atomic():
                return not bool(self.select_for_update(nowait=nowait))
        except Exception as e:
            self.log(logging.ERROR, f"it is in running. {e}")
            return True

    def queryset(self) -> "models.QuerySet":
        """
            Get queryset of one object
        """
        return self.__class__.objects.filter(id=self.id)

    def update_data(self, data: dict):
        """
            Update one object
        """
        return self.queryset().update(**data)
