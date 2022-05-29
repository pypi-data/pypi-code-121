import base64
import inspect
import logging
from types import ModuleType
from typing import Union


logger = logging.getLogger(__name__)


def make_udf(module_or_code: Union[ModuleType, str], *args, pycmd='python') -> str:
    '''
    This function takes a Python module or a code string,
    encodes the source code of the module or the code string
    into a byte string, which is suitable for transmission over the Internet,
    and returns a simple Python code snipplet that decodes and executes
    the original source code.

    Args:
        `module_or_code`: either a Python module *object* (not the module name),
            or a code block as a string.

            If the UDF is module `mypackage.udfs.udf`, then you may do

                import mypackage.udfs.udf
                s = make_udf(mypackage.udfs.udf)

            but not

                s = make_udf('mypackage.udfs.udf')

            If the UDF is a script that can not be imported by the package
            mechanism, you can read the content of the script into a string
            and pass that to `make_udf`. For example, suppose the UDF is
            a script named 'myudf.py' in the same directory as the
            (script or module) code in which you call `make_udf`, you
            can do

                from pathlib import Path
                code = (Path(__file__).parent / 'myudf.py').read_text()
                s = make_udf(code)

        `args`: if present, positional arguments to the UDF script.
            Each argument value should be a simple string or number
            (which will be converted to string)
            that does not contain any special characters (such as space,
            quotes) that could potentially cause trouble on the command-line.

            In this case, `module_or_code` processes a known number
            of arguments specified on the command-line before processing
            records coming from `stdin`.
            The number of args must be fixed; there can not be optional
            arguments with default values, because the UDF assumes data
            records begin after the known number of arguments.

            See `hive_udf_args_example.py` for an example.

        `pycmd`: the Python command on the Hive worker node, such as `python`, `python3`.

    Suppose `s` is the output of this function, then it is used like this
    to construct a HiveQL statement:

        sql = f"""
            SELECT
                TRANSFORM ( ...input_columns... )
                USING '{s}'
                AS (...output_columns...)
            FROM {db_name}.{table_name}
            WHERE ...
        """

    (The part after `FROM` may be a subquery rather than a table directly.)

    An important detail is that this string (`s`) is wrapped by single quotes
    in the HiveQL statement, as shown above.

    If `module_or_code` is a UDAF rather than UDF, a `CLUSTER BY` clause
    is needed, like this:

        sql = f"""
            SELECT
                TRANSFORM (
                    ...input_columns_including_aggregation_columns...
                    )
                USING '{s}'
                AS (...output_columns...)
            FROM (
                SELECT
                    ...columns_including_aggregation_columns...
                FROM {db_name}.{table_name}
                CLUSTER BY ...aggregation_columns...
                ) AS t
        """

    This function supports 4 scenarios:

        1. UDF
        2. UDAF
        3. UDF with arguments
        4. UDAF with arguments

    The difference between UDF and UDAF does not appear in this function,
    but rather in `module_or_code` and the HiveQL statements that use the
    output of this function (i.e. presence of `CLUSTER BY`).

    While the current function is written in Python 3.6+, the UDF `module_or_code`
    is written in the Python version that is installed on the Hive server.
    '''

    if inspect.ismodule(module_or_code):
        s = inspect.getsource(module_or_code)
    else:
        assert isinstance(module_or_code, str)
        s = module_or_code

    encoded = base64.urlsafe_b64encode(s.encode())

    script = 'import sys, base64; code = sys.argv[1]; code = base64.urlsafe_b64decode(code); code = code if sys.version_info[0] == 2 else code.decode(); exec(code);'

    code = f'{pycmd} -c "{script}" {str(encoded)[2:-1]}'

    if args:
        code = code + ' ' + ' '.join(str(v) for v in args)

    return code
