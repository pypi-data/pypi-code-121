"""add pg load_payload_tuples

Revision ID: 34490abd765c
Revises: 2efc91c0f0f6
Create Date: 2020-04-24 19:47:40.784157

"""

# revision identifiers, used by Alembic.
revision = "34490abd765c"
down_revision = "2efc91c0f0f6"
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa
import geoalchemy2


def upgrade():
    sql = """
CREATE OR REPLACE FUNCTION peek_storage_service.load_paylaod_tuples(
	sql_qry_ character varying,
	payload_filt_ character varying,
	loader_module_class_method_ character varying,
	python_path character varying,
	fetch_size_ integer DEFAULT 50)
    RETURNS character varying
    LANGUAGE 'plpython3u'

    COST 100
    VOLATILE 
    
AS $BODY$

import json
from base64 import b64decode
sqlQry = sql_qry_
payloadFilt = json.loads(payload_filt_)
loaderModuleClassMethod = loader_module_class_method_
pythonPath = json.loads(python_path)
fetchSize = fetch_size_

# ---------------
# Setup to use the virtual environment
import sys

sys.path.extend(pythonPath)

# ---------------
# Dynamically load the tuple create method

from importlib.util import find_spec, module_from_spec

modName, className, methodName = loaderModuleClassMethod.rsplit('.',2)

if modName in sys.modules:
	tuple_package = sys.modules[modName]

else:
	modSpec = find_spec(modName)
	if not modSpec:
		 raise Exception("Failed to find package %s,"
						   " is the python package installed?" % modName)
	tuple_package = modSpec.loader.load_module()

TupleClass = getattr(tuple_package, className)
tupleLoaderMethod = getattr(TupleClass, methodName)

# ---------------
# Turn a row["val"] into a row.val
class Wrap:
    row = None
    def __getattr__(self, name):
        return self.row[name]

wrap = Wrap()

# ---------------
# Iterate through and load the tuples
results = []

cursor = plpy.cursor(sqlQry)
while True:
    rows = cursor.fetch(max(500,fetchSize))
    if not rows:
        break
    for row in rows:
        wrap.row = row
        results.append(tupleLoaderMethod(wrap))

# ---------------
# Convert it to a payload

from vortex.Payload import Payload
encodedPayload = Payload(filt=payloadFilt, tuples=results) \
                        .toEncodedPayload() \
                        .decode() \
                        if results else None

return json.dumps({
    'count': len(results),
    'encodedPayload': encodedPayload
})

$BODY$;

ALTER FUNCTION peek_storage_service.load_paylaod_tuples(character varying, character varying, character varying, character varying, integer)
    OWNER TO peek;


          """
    op.execute(sql)


def downgrade():
    pass
