import io
import os
import zipfile
from localstack.utils.files import mkdir
from localstack_ext.bootstrap.pods.service_state import BackendState,ServiceKey,ServiceState
def get_path_for_backend(temporary_path:str,service_key:ServiceKey)->str:
 _temp_path=os.path.join(temporary_path,*service_key)
 mkdir(_temp_path)
 return _temp_path
class ServiceStateMarshaller:
 @staticmethod
 def marshal(state:ServiceState)->bytes:
  zip_buffer=io.BytesIO()
  with zipfile.ZipFile(zip_buffer,"a")as zip_file:
   for service_key,service_state in state.state.items():
    temp_path=os.path.join(*service_key)
    for backend_name,blob in service_state.backends.items():
     zip_file.writestr(os.path.join("api_states",temp_path,backend_name),blob)
  zip_buffer.seek(0)
  return zip_buffer.getvalue()
 @staticmethod
 def unmarshall(zip_content:bytes)->ServiceState:
  z=zipfile.ZipFile(io.BytesIO(zip_content))
  global_state=ServiceState()
  for f in z.namelist():
   splits=f.split("/")
   account,region,service,backend=splits[-4:]
   aux_backend=BackendState(key=ServiceKey(account,region,service),backends={backend:z.read(f)})
   global_state.add(aux_backend)
  return global_state
# Created by pyminifier (https://github.com/liftoff/pyminifier)
