_B='_ls_patch_applied'
_A=None
import inspect,os.path,sys,traceback
from importlib.abc import MetaPathFinder,SourceLoader
from importlib.util import spec_from_file_location
import pyaes
class DecryptionHandler:
	decryption_key:0
	def __init__(A,decryption_key):A.decryption_key=decryption_key
	def decrypt(C,content):D=pyaes.AESModeOfOperationCBC(C.decryption_key,iv='\x00'*16);B=pyaes.Decrypter(D);A=B.feed(content);A+=B.feed();A=A.partition(b'\x00')[0];return A
class EncryptedFileFinder(MetaPathFinder):
	decryption_handler:0
	def __init__(A,decryption_handler):A.decryption_handler=decryption_handler
	def find_spec(E,fullname,path,target=_A):
		C=fullname;A=path
		if A and not isinstance(A,list):A=list(getattr(A,'_path',[]))
		if not A:return _A
		F=C.split('.')[-1];D=os.path.join(A[0],F+'.py');B=D+'.enc'
		if not os.path.isfile(B):return _A
		if os.path.isfile(D):return _A
		return spec_from_file_location(C,B,loader=DecryptingLoader(B,E.decryption_handler))
class DecryptingLoader(SourceLoader):
	decryption_handler:0
	def __init__(A,encrypted_file,decryption_handler):A.encrypted_file=encrypted_file;A.decryption_handler=decryption_handler
	def get_filename(A,fullname):return A.encrypted_file
	def get_data(B,filename):
		with open(filename,'rb')as C:A=C.read()
		A=B.decryption_handler.decrypt(A);return A
def init_source_decryption(decryption_handler):sys.meta_path.insert(0,EncryptedFileFinder(decryption_handler));patch_traceback_lines();patch_inspect_findsource()
def patch_traceback_lines():
	if getattr(traceback.FrameSummary,_B,_A):return
	@property
	def A(self):
		A=self
		try:return B.fget(A)
		except Exception:A._line='';return A._line
	B=traceback.FrameSummary.line;setattr(traceback.FrameSummary,'line',A);traceback.FrameSummary._ls_patch_applied=True
def patch_inspect_findsource():
	if getattr(inspect,_B,_A):return
	def A(*A,**C):
		try:return B(*(A),**C)
		except Exception:return[],0
	B=inspect.findsource;inspect.findsource=A;inspect._ls_patch_applied=True