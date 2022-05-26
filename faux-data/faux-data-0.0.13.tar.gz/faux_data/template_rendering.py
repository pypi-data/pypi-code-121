import logging
import random
import re
from datetime import datetime, timedelta
from typing import List, Tuple

import dateutil
import pandas as pd
import yaml
from jinja2 import BaseLoader, Environment
from jinja2.exceptions import UndefinedError
from jinja2.runtime import StrictUndefined

log = logging.getLogger(__name__)

JINJA = Environment(loader=BaseLoader, undefined=StrictUndefined)


def render_template(template_str: str,
                    runtime_vars: dict) -> Tuple[str, dict[str:str]]:

    start, end = resolve_time_period(runtime_vars.get("start"),
                                     runtime_vars.get("end"))

    log.info(f"resolved start [{start}] and end [{end}] vars")

    if runtime_vars.get("start"):
        del runtime_vars["start"]
    if runtime_vars.get("end"):
        del runtime_vars["end"]

    builtin_vars = get_builtin_vars()
    ts_vars = get_ts_vars(start, end)
    builtin_vars.update(ts_vars)

    vars_ = resolve_variables(template_str, builtin_vars, runtime_vars)
    log.debug(f"final template vars: {vars_}")

    try:
        rendered_template = JINJA.from_string(template_str).render(vars_)
    except UndefinedError as e:
        raise TemplateRenderException(
            f"The template expected variables that were not provided - {e}")

    return rendered_template, vars_


def resolve_variables(template_str: str, builtin_vars: dict,
                      runtime_vars: dict):
    """Resolve the template variables using the builtin and runtime provided variables.
    Returns the final set of vars to be applied to the template"""

    variable_lines = extract_variable_lines(template_str)
    builtin_vars.update(runtime_vars)
    vars_ = builtin_vars.copy()

    if not variable_lines:
        # no vars in template so just return builtins plus runtime vars
        return vars_

    for variable_line in variable_lines:
        rendered_var_line = JINJA.from_string(variable_line).render(vars_)
        var = yaml.safe_load(rendered_var_line)

        key = list(var)[0]  # get the key of the only element
        if key not in vars_:
            vars_.update(var)

    return vars_


def extract_variable_lines(template_str: str) -> List[str] | None:
    """Extracts the variables from a template as a list of strings"""

    pattern = r"(?:^variables:)(.*)(?:^tables:)"
    r = re.search(pattern, template_str, re.DOTALL | re.MULTILINE)

    if r:
        lines = r.group(1).splitlines()
        return [line.strip() for line in lines if line.strip() != ""]
    else:
        # no variables in this template
        return None


def get_builtin_vars():

    now = datetime.now()

    builtin_vars = {
        'today': now.date(),
        'now': now,
        'utcnow': now.astimezone(dateutil.tz.UTC),
        'delta': timedelta,
        'tomorrow': now.date() + timedelta(days=1),
        'yesterday': now.date() - timedelta(days=1),
        'randint': random.randint,
        'nowint': int(now.timestamp())
    }

    return builtin_vars


def get_ts_vars(start, end):
    return {
        'start': start,
        'end': end,
        'start_int': int(start.timestamp()),
        'end_int': int(end.timestamp()),
        'start_ymd': start.strftime("%Y-%m-%d"),
        'end_ymd': end.strftime("%Y-%m-%d")
    }


def parse_input_ts(ts):
    """Parse the input to either a dattime, or Timedelta"""
    if ts is None or ts == "":
        return None
    else:
        try:
            res = dateutil.parser.isoparse(ts)
        except Exception as e:
            try:
                res = pd.Timedelta(ts)
            except Exception as e2:
                raise TemplateRenderException(
                    f"Unable to parse [{ts}] as timedelta (Err: {e2}) or timestamp (Err: {e})"
                )
    return res


def resolve_time_period(start, end):
    """Resolves the start and end values that will be used in the template.

    If not provided:
        start defaults to the start of yesterday
        end defaults to the end of yesterday

    If just start is provided:
        If start is a iso datetime it'll define the start of the time period, the end will be 1 day in future
        If start is a positive offset it'll be added onto `now`, the end will be 1 day in future
        If start is a negative offset it'll be subtracted from `now`, and the end will be `now`

    If just end is provided:
    """

    # parse the inputs
    start = parse_input_ts(start) if start else None
    end = parse_input_ts(end) if end else None

    # default size of timeperiod
    period = timedelta(days=1)
    now = datetime.now()

    # TODO: can pattern matching tidy this up?

    if start is None and end is None:
        # neither provided, default to 'yesterday'
        end = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return end - period, end

    if start is None and end is not None:
        # only end is provided
        if isinstance(end, datetime):
            return end - period, end

        elif isinstance(end, pd._libs.tslibs.timedeltas.Timedelta):

            if end.total_seconds() >= 0:
                # end is a positive delta
                return now, now + end

            else:
                # end is a negative delta
                end = now + end
                return end - period, end

    elif start is not None and end is None:
        # only start is provided
        if isinstance(start, datetime):
            return start, start + period

        elif isinstance(start, pd._libs.tslibs.timedeltas.Timedelta):

            if start.total_seconds() >= 0:
                # start is a positive delta
                start = now + start
                return start, start + period

            else:
                # start is a negative delta
                return now + start, now

    else:
        # start and end are both provided

        if isinstance(start, datetime) and isinstance(end, datetime):
            return start, end

        elif isinstance(start, pd._libs.tslibs.timedeltas.Timedelta) \
            and isinstance(end, pd._libs.tslibs.timedeltas.Timedelta):
            return now + start, now + end

        elif isinstance(start, datetime) \
            and isinstance(end, pd._libs.tslibs.timedeltas.Timedelta):

            return start, start + end

        elif isinstance(start, pd._libs.tslibs.timedeltas.Timedelta) \
            and isinstance(end, datetime):

            return end + start, end

    raise TemplateRenderException(
        f"Expected input types to be either datetime or Timedelta but start was [{type(start)}] and end was [{type(end)}]"
    )


class TemplateRenderException(Exception):
    pass
