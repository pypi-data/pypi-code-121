"""up1_run_generic_py

Revision ID: 51e48a6594d5
Revises: 72518909970f
Create Date: 2020-06-02 22:27:48.650874

"""

# revision identifiers, used by Alembic.
revision = "51e48a6594d5"
down_revision = "72518909970f"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    sql = """

DROP FUNCTION IF EXISTS
              peek_storage_service.run_generic_python(character varying,
                                              character varying,
                                              character varying,
                                              character varying);

CREATE OR REPLACE FUNCTION peek_storage_service.run_generic_python(
    args_tuple_json_str character varying,
    class_method_to_run_str_ character varying,
    class_method_to_import_tuples_ character varying,
    python_path character varying)
    RETURNS character varying
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE

AS $BODY$

import json
from base64 import b64decode
argsTupleJsonStr = args_tuple_json_str
classMethodToRunStr = class_method_to_run_str_
classMethodToImportTuplesStr = class_method_to_import_tuples_
pythonPath = json.loads(python_path)

# ---------------
# Setup to use the virtual environment
import sys

sys.path.extend(pythonPath)

from importlib.util import find_spec, module_from_spec

# ---------------
# Dynamically load the import tuple method

if classMethodToImportTuplesStr and classMethodToImportTuplesStr != 'None':
    modName, className, methodName = classMethodToImportTuplesStr.rsplit('.',2)

    if modName in sys.modules:
        package_ = sys.modules[modName]

    else:
        modSpec = find_spec(modName)
        if not modSpec:
             raise Exception("Failed to find package %s,"
                             " is the python package installed?" % modName)
        package_ = modSpec.loader.load_module()

    Class_ = getattr(package_, className)
    importTupleMethod = getattr(Class_, methodName)
    importTupleMethod()

# ---------------
# Dynamically load the tuple create method

modName, className, methodName = classMethodToRunStr.rsplit('.',2)

if modName in sys.modules:
    package_ = sys.modules[modName]

else:
    modSpec = find_spec(modName)
    if not modSpec:
         raise Exception("Failed to find package %s,"
                         " is the python package installed?" % modName)
    package_ = modSpec.loader.load_module()

Class_ = getattr(package_, className)
classMethodToRun = getattr(Class_, methodName)

# ---------------
# Load the arguments

from peek_storage_service.plpython.RunPyInPg import _RunPyInPgResultTuple, _RunPyInPgArgTuple

argsTuple = _RunPyInPgArgTuple()._fromJson(argsTupleJsonStr)

# ---------------
# Run the method

result = classMethodToRun(plpy, *argsTuple.args, **argsTuple.kwargs)

# ---------------
# Return the result

return _RunPyInPgResultTuple(result=result)._toJson()

$BODY$;

ALTER FUNCTION peek_storage_service.run_generic_python(character varying,
                                               character varying,
                                               character varying,
                                               character varying)
    OWNER TO peek;


          """
    op.execute(sql)


def downgrade():
    pass
