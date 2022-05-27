# -*- coding: utf8 -*-

"""
Utilitats compartides pels diferents processos.
Quan s'importa per primera vegada executa les següents accions:
    copyreg per permetre multiprocessing amb mètodes de classes
    elimina els warnings del client de MariaDB
"""

import copyreg
import datetime as d
import dateutil.easter as e
import jdcal as j
import types
import multiprocessing
import multiprocessing.pool
import MySQLdb
import warnings

from .constants import IS_PYTHON_3  # noqa
from .database import Database  # noqa
from .mail import Mail  # noqa
from .redis import Redis  # noqa
from .ssh import SSH, SFTP  # noqa
from .textfile import TextFile  # noqa


if IS_PYTHON_3:
    """
    Modificació de Pool per utilitzar processos non-daemonic
    i així poder tenir fills.
    https://stackoverflow.com/questions/6974695/python-process-pool-non-daemonic
    """
    class NoDaemonProcess(multiprocessing.Process):

        @property
        def daemon(self):
            return False

        @daemon.setter
        def daemon(self, value):
            pass

    class NoDaemonContext(type(multiprocessing.get_context())):

        Process = NoDaemonProcess

    class NoDaemonPool(multiprocessing.pool.Pool):

        def __init__(self, *args, **kwargs):
            kwargs['context'] = NoDaemonContext()
            super(NoDaemonPool, self).__init__(*args, **kwargs)
else:
    class NoDaemonProcess(multiprocessing.Process):

        def _get_daemon(self):
            return False

        def _set_daemon(self, value):
            pass

        daemon = property(_get_daemon, _set_daemon)

    class NoDaemonPool(multiprocessing.pool.Pool):

        Process = NoDaemonProcess


def years_between(inici, final):
    """Calcula els anys entre dues dates."""
    residu = (final.month, final.day) < (inici.month, inici.day)
    return final.year - inici.year - residu


def gcal2jd(gcal):
    """Converteix gcal en jd."""
    return int(sum(j.gcal2jd(gcal.year, gcal.month, gcal.day)) + 0.5)


def jd2gcal(jd):
    """Converteix jd en gcal."""
    return d.date(*j.jd2gcal(2400000.5, jd - 2400001)[:3])


def is_weekend(data):
    """Respon si la data és un cap de setmana."""
    return data.weekday() in (5, 6)


def is_working_day(data):
    """Respon si la data és festiu."""
    year = data.year
    dv_s = e.easter(year) + d.timedelta(days=-2)
    dl_s = e.easter(year) + d.timedelta(days=+1)
    dies = ((1, 1), (6, 1), (1, 5), (24, 6), (15, 8), (11, 9), (12, 10),
            (1, 11), (6, 12), (8, 12), (25, 12), (26, 12))
    festius = [dv_s, dl_s] + [d.date(year, mes, dia) for (dia, mes) in dies]
    return data not in festius and not is_weekend(data)


def _pickle_method(method):
    """copyreg."""
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    """copyreg."""
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)
warnings.filterwarnings('ignore', category=MySQLdb.Warning)
