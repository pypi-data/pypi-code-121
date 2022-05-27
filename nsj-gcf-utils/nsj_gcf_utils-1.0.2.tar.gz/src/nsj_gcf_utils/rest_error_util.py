from nsj_gcf_utils  .exception import ERPException
from nsj_gcf_utils.json_util import json_dumps, json_loads
from pydantic import ValidationError
from typing import Dict, List, Union, Tuple


def _format_tuple_error(error: Tuple[str, str]):
    return {
        'code': error[0],
        'message': error[1]
    }


def _format_erpexception_error(error: ERPException):
    return {
        'code': error.mope_code,
        'message': error.message
    }


def _format_list_error(error: Union[List[Tuple[str, str]], List[ERPException]]):
    result = []
    for e in error:
        if isinstance(e, tuple):
            formated = _format_tuple_error(e)
        elif isinstance(e, ERPException):
            formated = _format_erpexception_error(e)
        elif isinstance(e, str):
            e = (None, e)
            formated = _format_tuple_error(e)
        elif isinstance(e, Exception):
            e = (None, f'{e}')
            formated = _format_tuple_error(e)
        else:
            formated = _format_unknow_error()

        result.append(formated)

    return result


def _format_unknow_error():
    return {
        'code': None,
        'message': 'Erro desconhecido'
    }


def _format_pydantic_validation_error(error: ValidationError):
    result = []
    errors = json_loads(error.json())
    for e in errors:
        msg = f"Erro de validando campo '{e['loc'][0]}' de entrada. Mensagem do erro: {e['msg']}."
        e_tuple = (None, msg)
        result.append(_format_tuple_error(e_tuple))

    return result


def format_error_body(
    error: Union[
        Tuple[str, str],
        List[Tuple[str, str]],
        ERPException,
        List[ERPException],
        str,
        Exception,
        List[str],
        List[Exception],
        ValidationError
    ]
) -> List[Dict[str, str]]:

    if isinstance(error, tuple):
        return [_format_tuple_error(error)]
    elif isinstance(error, list):
        return _format_list_error(error)
    elif isinstance(error, ERPException):
        return [_format_erpexception_error(error)]
    elif isinstance(error, str):
        error = (None, error)
        return [_format_tuple_error(error)]
    elif isinstance(error, ValidationError):
        return _format_pydantic_validation_error(error)
    elif isinstance(error, Exception):
        error = (None, f'{error}')
        return [_format_tuple_error(error)]
    else:
        return [_format_unknow_error()]


def format_json_error(
    error: Union[
        Tuple[str, str],
        List[Tuple[str, str]],
        ERPException,
        List[ERPException],
        str,
        Exception,
        List[str],
        List[Exception],
        ValidationError
    ]
) -> List[Dict[str, str]]:
    return json_dumps(format_error_body(error))
