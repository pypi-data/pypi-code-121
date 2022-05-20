import click
import csv
import datetime
import io
import yaml
from decimal import Decimal
from json import dumps
from typing import Any, List, Type, Callable, Dict, Iterator, Optional, TypeVar

from pydantic import BaseModel

from dnastack.client.result_iterator import ResultIterator
from dnastack.feature_flags import in_global_debug_mode


class ConversionError(RuntimeError):
    """ Raised when the data conversion fails """


def normalize(content: Any, map_decimal: Type = str) -> Any:
    """
    Normalize the content for data export

    .. note: This is not designed for two-way data conversion.
    """
    if isinstance(content, Decimal):
        return map_decimal(content)
    elif isinstance(content, BaseModel):
        return normalize(content.dict(), map_decimal=map_decimal)
    elif isinstance(content, dict):
        # Handle a dictionary
        return {
            k: normalize(v, map_decimal=map_decimal)
            for k, v in content.items()
        }
    elif isinstance(content, (tuple, list, set, ResultIterator)):
        # Handle a list or tuple or set or anything iterable
        return [normalize(i, map_decimal=map_decimal) for i in content]
    elif (isinstance(content, datetime.datetime)
          or isinstance(content, datetime.date)
          or isinstance(content, datetime.time)):
        return content.isoformat()
    else:
        return content


I = TypeVar('I')
R = TypeVar('R')


def display_result_iterator(iterator: Iterator[Dict[str, Any]],
                            transform: Optional[Callable[[I], R]] = None,
                            limit: Optional[int] = None) -> int:
    """ Display the result from the iterator """
    row_count = 0

    for row in iterator:
        if row_count >= limit:
            break

        if row_count == 0:
            # First row
            click.echo('[')
        else:
            # Clean up from the previous iteration.
            click.echo(',', nl=False)
            click.secho(f' # {row_count}', dim=True, err=True)

        entry = transform(row) if transform else row
        click.echo('\n'.join([f'  {line}' for line in dumps(entry, indent=2).split('\n')]), nl=False)

        row_count += 1

    click.echo('\n]')

    return row_count


def to_json(content: Any):
    try:
        return dumps(content, indent=2)
    except Exception:
        raise ConversionError(f'Failed to convert {content} as JSON string')


def to_csv(object_list: List[dict]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    # if we have at least one result, add the headers
    if len(object_list) > 0:
        writer.writerow(object_list[0].keys())

    for res in object_list:
        data_row = list(map(lambda x: str(x).replace(",", r'\\,'), res.values()))
        writer.writerow(data_row)

    return output.getvalue()
