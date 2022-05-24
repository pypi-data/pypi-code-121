import io,os,zipfile
from localstack.utils.files import mkdir
from localstack_ext.bootstrap.pods.service_state import BackendState,ServiceKey,ServiceState
def get_path_for_backend(temporary_path,service_key):A=os.path.join(temporary_path,*(service_key));mkdir(A);return A
class ServiceStateMarshaller:
	@staticmethod
	def marshal(state):
		A=io.BytesIO()
		with zipfile.ZipFile(A,'a')as B:
			for (C,D) in state.state.items():
				E=os.path.join(*(C))
				for (F,G) in D.backends.items():B.writestr(os.path.join('api_states',E,F),G)
		A.seek(0);return A.getvalue()
	@staticmethod
	def unmarshall(zip_content):
		A=zipfile.ZipFile(io.BytesIO(zip_content));B=ServiceState()
		for C in A.namelist():D=C.split('/');E,F,G,H=D[-4:];I=BackendState(key=ServiceKey(E,F,G),backends={H:A.read(C)});B.add(I)
		return B