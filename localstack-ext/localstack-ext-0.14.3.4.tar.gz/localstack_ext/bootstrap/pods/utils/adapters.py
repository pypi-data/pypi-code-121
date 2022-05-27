import io,os,zipfile
from localstack.utils.files import mkdir
from localstack_ext.bootstrap.pods.service_state import BackendState,ServiceKey,ServiceState
def get_path_for_backend(temporary_path,service_key):A=os.path.join(temporary_path,*(service_key));mkdir(A);return A
class ServiceStateMarshaller:
	@staticmethod
	def marshal(state):
		C=state;A=io.BytesIO()
		with zipfile.ZipFile(A,'a')as D:
			for (B,G) in C.state.items():
				H=os.path.join(B.account_id,B.service,B.region)
				for (I,J) in G.backends.items():D.writestr(os.path.join('api_states',H,I),J)
			for (K,L) in C.assets.items():
				E=zipfile.ZipFile(io.BytesIO(L))
				for F in E.namelist():D.writestr(os.path.join(K,F),E.read(F))
		A.seek(0);return A.getvalue()
	@staticmethod
	def unmarshall(zip_content):
		B=zipfile.ZipFile(io.BytesIO(zip_content));C=ServiceState()
		def D():D=A.split('/');E,F,G,H=D[-4:];I=BackendState(key=ServiceKey(E,G,F),backends={H:B.read(A)});C.add(I)
		def E():D=A.split('/')[0];C.add_asset(service=D,content=B.read(A))
		for A in B.namelist():
			if A.startswith('api_'):D()
			else:E()
		return C