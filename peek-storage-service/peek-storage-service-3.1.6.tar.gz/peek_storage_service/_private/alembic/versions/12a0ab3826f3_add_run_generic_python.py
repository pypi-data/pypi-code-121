"""add run_generic_python

Revision ID: 12a0ab3826f3
Revises: 34490abd765c
Create Date: 2020-04-25 15:28:50.279318

"""

# revision identifiers, used by Alembic.
revision = "12a0ab3826f3"
down_revision = "34490abd765c"
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    sql = """
CREATE OR REPLACE FUNCTION peek_storage_service.run_generic_python(
    args_json character varying,
    kwargs_json character varying,
    class_method_to_run_str_ character varying,
    python_path character varying)
    RETURNS character varying
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    
AS $BODY$

import json
from base64 import b64decode
args = json.loads(args_json)
kwargs = json.loads(kwargs_json)
classMethodToRunStr = class_method_to_run_str_
pythonPath = json.loads(python_path)

# ---------------
# Setup to use the virtual environment
import sys

sys.path.extend(pythonPath)

# ---------------
# Dynamically load the tuple create method

from importlib.util import find_spec, module_from_spec

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

result = classMethodToRun(plpy, *args, **kwargs)

return json.dumps({
    'result': result
})

$BODY$;

ALTER FUNCTION peek_storage_service.run_generic_python(character varying, character varying, character varying, character varying)
    OWNER TO peek;


          """
    op.execute(sql)


def downgrade():
    sql = """DROP FUNCTION peek_storage_service.run_generic_python(character varying, 
                                                            character varying, 
                                                            character varying, 
                                                            character varying);"""
    op.execute(sql)
