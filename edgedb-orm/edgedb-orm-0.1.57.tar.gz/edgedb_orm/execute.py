import typing as T
import time
import orjson
from devtools import debug
import edgedb
from .span import safe_span

MUTATION_ACTIONS = ["insert ", "update ", "delete "]


class ExecuteException(Exception):
    pass


def operation_from_query_str(query_str: str) -> str:
    s = query_str.lower()
    for action in MUTATION_ACTIONS:
        if action in s:
            return "mutation"
    return "query"


async def query(
    client: edgedb.AsyncIOClient,
    query_str: str,
    variables: T.Optional[T.Dict[str, T.Any]] = None,
    only_one: bool = False,
    print_query: bool = True,
    print_variables: bool = False,
    print_raw_results: bool = False,
) -> T.Optional[dict]:
    """Returns a json str to be parsed by pydantic raw. Errors are raised by the lib!"""
    if not variables:
        variables = {}
    query_func = client.query_json if not only_one else client.query_single_json
    start = time.time()
    try:
        with safe_span(
            op=f"edgedb.{operation_from_query_str(query_str)}",
            description=query_str[:200],
        ):
            j_str = await query_func(query=query_str, **variables)
        with safe_span(op="orjson.loads", description=f"len str: {len(j_str)}"):
            j = orjson.loads(j_str)
        if print_raw_results:
            debug(j)
    except edgedb.errors.ConstraintViolationError as e:
        print(f"{e=}")
        if "is prohibited by link target policy" in str(e):
            raise e
        if "violates exclusivity constraint" in str(e):
            field_name = str(e).split(" ")[0].replace("_", " ")
            raise ExecuteException(f"That {field_name} already exists in our system.")
        raise e
    except Exception as e:
        print(
            f"EdgeDB Query Exception: {e}, query_str and variables: {query_str=}, {variables=}"
        )
        raise e
    took_ms = (time.time() - start) * 1000
    print_s = ""
    if print_query:
        print_s += f" {query_str=} "
    if print_variables:
        print_s += f" {variables=} "
    if print_s:
        print_s = print_s.strip()
        print(print_s)
    print(f"took {took_ms}")
    return j
