from datetime import datetime
import pytz
from dateutil.relativedelta import *
import calendar
import typing

DIAS_GRACIA = 20
DIAS_ANTICIPO_DE_PAGO = 7
MID_DAY_HOUR = 12


arg_tz = pytz.timezone("America/Buenos_Aires")


def readable_date(f: datetime) -> str:
    """ Convierte una variable de tipo datetime.datetime al formato DD-MM-YYYY

    :param f: valor a convertir
    :type f: datetime
    :return: fecha formateada DD-MM-YYYY
    :rtype: str
    """
    return f.strftime("%d-%m-%Y")


def string_to_datetime(mongo_date: typing.Union[str, datetime]) -> datetime:
    """ Convierte un string a datetime

    :param mongo_date: Fecha a convertir
    :type mongo_date: str | datetime
    :return: Hora local
    :rtype: datetime
    """
    if type(mongo_date) == str:
        try:
            a = datetime.strptime(mongo_date, '%Y-%m-%dT%H:%M:%S.%f%z').astimezone(arg_tz)
        except:
            a = datetime.strptime(mongo_date, '%Y-%m-%dT%H:%M:%S%z').astimezone(arg_tz)
        return a
    else:
        mongo_date = arg_tz.localize(mongo_date + relativedelta(hours=-1))
        return mongo_date


def store_datetime_as_string(new_date: datetime) -> str:
    """ Convierte la fecha dada a string

    :param new_date: Fecha a convertir
    :type new_date: datetime.datetime
    :return: el valor recibido por parametro como string
    :rtype: str
    """
    a = new_date.astimezone(arg_tz)
    a = str(a).replace(" ", "T")  # todo    ESTA FORMULA TODAVÍA NO SIRVE.
    return a


def localize(utc_datetime: datetime) -> datetime:
    """ Convierte UTC a hora local

    :param utc_datetime: datetime en UTC+0
    :type utc_datetime: datetime
    :return: Hora recibida por parametro convertida a UTC+3 (hora local)
    :rtype: datetime
    """
    aware = utc_datetime.replace(tzinfo=pytz.utc)
    local_datetime = aware.astimezone(arg_tz)
    return local_datetime


def set_next_vigency(next_payment_date: datetime) -> datetime:
    """ Establece la fecha de vigencia

    :param next_payment_date: Fecha del proximo pago
    :type next_payment_date: datetime
    :return: Fecha de vigencia segun la fecha del proximo pago
    :rtype: datetime
    """
    return (next_payment_date + relativedelta(days = DIAS_GRACIA + DIAS_ANTICIPO_DE_PAGO))


def get_periodo(source_date) -> str:
    """ Obtener el periodo a partir de una fecha de pago

    :param source_date:  datetime en UTC+0
    :type source_date: datetime
    :return: periodo actual con el formato MM/YYYY
    :rtype: str
    """
    period_init = source_date
    month = period_init.month
    year = period_init.year
    return f"{month}/{year}"


def calculate_payment_date(pid: int, cobro: str, pub: str) -> datetime:
    """ Calcula el próximo día de pago para un cliente según la fecha de inicio de período.

    :param pid: Period Init Day - día del mes que inicia el periodo del usuario
    :type period_init_day: int
    :param cobro: los valores posibles son Mensual, Trimestral, Cuatrimestral, Semestral, Anual
    :type cobro: str
    :param pub: Periodo Última Boleta - el período de la última boleta existente para este usuario
    :type pub: str
    :return: Fecha de pago
    :rtype: datetime
    """
    month, year = [int(a) for a in pub.split('/')]
    last_period_date = datetime(year=year, month=month, day=1)
    duration_map = {"Mensual": 1, "Trimestral": 3, "Cuatrimestral": 4, "Semestral": 6, "Anual": 12}
    npd_aux = (last_period_date + relativedelta(months=duration_map[cobro]))
    npd = replace_day_in_period(npd_aux.year, npd_aux.month, pid)
    next_payment_date = npd - relativedelta(days=DIAS_ANTICIPO_DE_PAGO)
    return next_payment_date


def last_payment_date_adjust(client):
    day = client["period_init_day"]
    proposed = today_argentina() + relativedelta(days=DIAS_ANTICIPO_DE_PAGO)

    if proposed.day >= day:
        dif = proposed.day - day
    else:
        prev_month = proposed - relativedelta(months=1)
        month_days = calendar.monthrange(prev_month.year, prev_month.month)[1]
        dif = month_days - day + proposed.day
    return proposed - relativedelta(days=dif)


def today_argentina():
    return pytz.utc.localize(datetime.utcnow()).astimezone(arg_tz)


def replace_day_in_period(year: int, month: int, day: int):
    """ Calcula el próximo día de pago para un cliente según la fecha de inicio de período.

       :param year: año
       :type year: int
       :param month: mes
       :type month: int
       :param day: dia del mes que se pretende reemplazar en el periodo mes/año
       :type day: int
       :return: Fecha ajustada al periodo
       :rtype: datetime
       """
    try:
        date = datetime(year=year, month=month, day=day)
    except ValueError:
        end_of_month = calendar.monthrange(year, month)[1]
        date = datetime(year=year, month=month, day=end_of_month)
    return date


def get_periodo_anterior(cobro, periodo) -> str:
    """ Obtener el periodo a partir de una fecha de pago

    :param source_date:  datetime en UTC+0
    :type source_date: datetime
    :return: periodo actual con el formato MM/YYYY
    :rtype: str
    """
    month, year = [int(a) for a in periodo.split('/')]
    last_period_date = datetime(year=year, month=month, day=1)
    duration_map = {"Mensual": 1, "Trimestral": 3, "Cuatrimestral": 4, "Semestral": 6, "Anual": 12}
    aux = (last_period_date - relativedelta(months=duration_map[cobro]))
    month, year = aux.month, aux.year
    return f"{month}/{year}"


