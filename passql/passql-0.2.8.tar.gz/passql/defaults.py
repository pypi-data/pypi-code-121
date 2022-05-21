from passql.sql import SqlConverter
from types import GeneratorType
import datetime

__all__ = (
    'SqlDefaultConverters',
)


class SqlDefaultConverters:
    COMMON = SqlConverter({
        int: lambda val, _: str(val),
        float: lambda val, _: str(val),
        bool: lambda val, _: "TRUE" if val else "FALSE",
        type(None): lambda val, _: "NULL",
    })

    POSTGRES = COMMON + SqlConverter({
        str: lambda val, converter: "'" + val.replace("'", "") + "'::text",
        tuple: lambda val, converter: ','.join(converter(v) for v in val),
        range: lambda val, converter: ','.join(converter(v) for v in val),
        GeneratorType: lambda val, converter: ','.join(converter(v) for v in val),
        list: lambda val, converter: "'{" + ','.join(converter(v)
                                                     if type(v) is not str
                                                     else ("\"" + v.replace("\"", "") + "\"")
                                                     for v in val) + "}'",
        set: lambda val, converter: "'{" + ','.join(converter(v)
                                                    if type(v) is not str
                                                    else ("\"" + v.replace("\"", "") + "\"")
                                                    for v in val) + "}'",
        datetime.datetime: lambda val, converter: f"'{val}'::timestamp",
        datetime.date: lambda val, converter: f"'{val}'::date",
    })
