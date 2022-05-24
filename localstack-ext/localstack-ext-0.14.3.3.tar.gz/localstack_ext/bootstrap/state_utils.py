_A='__dict__'
import logging,os
from typing import Any,Callable,List,OrderedDict,Set,Tuple
import dill
from localstack.utils.common import ObjectIdHashComparator
from localstack.utils.files import rm_rf
API_STATES_DIR='api_states'
KINESIS_DIR='kinesis'
DYNAMODB_DIR='dynamodb'
POD_KEEP='.podkeep'
LOG=logging.getLogger(__name__)
def check_already_visited(obj,visited):
	A=visited
	if hasattr(obj,_A):
		A=A or set();B=ObjectIdHashComparator(obj)
		if B in A:return True,A
		A.add(B)
	return False,A
def get_object_dict(obj):
	A=obj
	if isinstance(A,dict):return A
	B=getattr(A,_A,None);return B
def is_composite_type(obj):return isinstance(obj,(dict,OrderedDict))or hasattr(obj,_A)
def api_states_traverse(api_states_path,side_effect,mutables):
	C=side_effect
	for (A,K,F) in os.walk(api_states_path):
		for D in F:
			try:B=os.path.normpath(A).split(os.sep);G=B[-1];H=B[-2];I=B[-3];C(dir_name=A,fname=D,region=H,service_name=G,account_id=I,mutables=mutables)
			except Exception as J:
				E=f"Failed to apply {C.__name__} for {D} in dir {A}: {J}";LOG.warning(E)
				if LOG.isEnabledFor(logging.DEBUG):LOG.exception(E)
				continue
def load_persisted_object(state_file):
	A=state_file
	if not os.path.isfile(A):return
	import dill
	with open(A,'rb')as B:
		try:C=B.read();D=dill.loads(C);return D
		except Exception as E:LOG.debug('Unable to read pickled persistence file %s: %s',A,E)
def persist_object(obj,state_file):
	with open(state_file,'wb')as A:B=A.write(dill.dumps(obj));return B
def cleanse_keep_files(file_path):
	for (B,D,C) in os.walk(file_path):
		for A in C:
			if A==POD_KEEP:rm_rf(os.path.join(B,A))
def populate_empty_dirs(file_path):
	for (B,C,G) in os.walk(file_path):
		for D in C:
			A=os.path.join(B,D);E=list((B for B in os.listdir(A)if os.path.isfile(os.path.join(A,B))))
			if not E:
				F=os.path.join(A,POD_KEEP)
				with open(F,'w'):0