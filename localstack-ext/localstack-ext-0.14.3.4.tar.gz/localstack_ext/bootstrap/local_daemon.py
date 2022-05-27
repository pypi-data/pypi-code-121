#!/usr/bin/env python
_G='uname -a'
_F='Unsupported operation "%s"'
_E='Terminating local daemon process (port %s)'
_D='result'
_C='Content-Length'
_B='error'
_A=True
import json,logging,os,shutil,socket,struct,subprocess,sys,tempfile,threading,traceback,uuid
from http.server import BaseHTTPRequestHandler,HTTPServer
from socketserver import ThreadingMixIn
import boto3,requests
from localstack.utils.common import is_port_open
LOG=logging.getLogger('local_daemon')
DEFAULT_PORT_LOCAL_DAEMON=4600
DEFAULT_PORT_LOCAL_DAEMON_ROOT=4601
DEFAULT_PORT_S3=4566
DEFAULT_PORT_EC2=4566
ENDPOINT_S3=f"http://localhost:{DEFAULT_PORT_S3}"
ENDPOINT_EC2=f"http://localhost:{DEFAULT_PORT_EC2}"
LOCAL_BIND_ADDRESS_PATTERN='192.168.123.*'
USED_BIND_ADDRESSES=set()
MAC_NETWORK_INTERFACE='en0'
BUCKET_MARKER_LOCAL=(os.environ.get('BUCKET_MARKER_LOCAL')or'').strip()or'__local__'
class FuncThread(threading.Thread):
	def __init__(A,func,params=None):threading.Thread.__init__(A);A.daemon=_A;A.params=params;A.func=func
	def run(A):
		try:A.func(A.params)
		except Exception as B:log('Error in thread function: %s %s'%(B,traceback.format_exc()))
class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):daemon_threads=_A
class RequestHandler(BaseHTTPRequestHandler):
	def do_POST(A):
		A.read_content()
		try:B=A.handle_request();A.send_response(200)
		except Exception as C:D=str(C);B=json.dumps({_B:D});log('Error handling request: %s - %s'%(A.request_json,C));A.send_response(500)
		A.send_header(_C,'%s'%len(B)if B else 0);A.end_headers()
		if len(B or''):A.wfile.write(to_bytes(B))
	def handle_request(D):
		C=D.request_json;A='{}';B=C.get('op','')
		if B=='getos':A={_D:get_os()}
		elif B=='shell':E=C.get('command');A=run_shell_cmd(E)
		elif B=='s3:download':A=s3_download(C)
		elif B.startswith('root:'):A=forward_root_request(C)
		elif B=='kill':log(_E%DEFAULT_PORT_LOCAL_DAEMON);os._exit(0)
		else:A={_B:_F%B}
		A=json.dumps(A)if isinstance(A,dict)else A;return A
	def read_content(A):
		if hasattr(A,'data_bytes'):return
		B=A.headers.get(_C);A.data_bytes=A.rfile.read(int(B));A.request_json={}
		try:A.request_json=json.loads(A.data_bytes)
		except Exception:pass
class RequestHandlerRoot(RequestHandler):
	def handle_request(D):
		C=D.request_json;A='{}';B=C.get('op')
		if B=='root:ssh_proxy':A=start_ssh_forward_proxy(C)
		elif B=='kill':log(_E%DEFAULT_PORT_LOCAL_DAEMON_ROOT);os._exit(0)
		else:A={_B:_F%B}
		A=json.dumps(A)if isinstance(A,dict)else A;return A
def s3_download(request):
	B=request;C=B['bucket'];D=B['key'];E=os.environ.get('TMPDIR')or tempfile.mkdtemp();A=os.path.join(E,B.get('file_name')or's3file.%s'%str(uuid.uuid4()))
	if not os.path.exists(A)or B.get('overwrite'):
		if C==BUCKET_MARKER_LOCAL:shutil.copy(D,A)
		else:F=boto3.client('s3',endpoint_url=ENDPOINT_S3);log('Downloading S3 file s3://%s/%s to %s'%(C,D,A));F.download_file(C,D,A)
	return{'local_file':A}
def forward_root_request(request):A=f"http://localhost:{DEFAULT_PORT_LOCAL_DAEMON_ROOT}";B=requests.post(A,data=json.dumps(request));return json.loads(to_str(B.content))
def start_ssh_forward_proxy(options):E='port';A=options;from localstack_ext.bootstrap.tcp_proxy import server_loop as F;B=22;C=A.get(E)or get_free_tcp_port();D=next_available_bind_address(B);log(f"Starting local SSH forward proxy, {D}:{B} -> localhost:{C}");A={'bind_port':B,'bind_addr':D,E:C};FuncThread(F,A).start();return{'host':D,'forward_port':C}
def next_available_bind_address(port):
	B=port;C=len(USED_BIND_ADDRESSES)+2
	for E in range(C,C+30):
		A=LOCAL_BIND_ADDRESS_PATTERN.replace('*',str(E));create_network_interface_alias(A)
		if is_port_open(f"tcp://{A}:{B}"):continue
		D=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		with D:
			try:D.bind((A,B))
			except Exception:continue
		USED_BIND_ADDRESSES.add(A);return A
	raise Exception(f"Unable to determine free bind address for port {B}")
def create_network_interface_alias(address,interface=None):
	B=address;A=interface;E='sudo'
	if is_mac_os():A=A or MAC_NETWORK_INTERFACE;run_cmd(f"{E} ifconfig {A} alias {B}");return
	if is_linux():
		C=os.listdir('/sys/class/net/');C=[A for A in C if':'not in A]
		for A in C:
			try:D=get_ip_address(A);log(f"Found network interface {A} with address {D}");assert D;assert A not in['lo']and not D.startswith('127.');run_cmd(f"{E} ifconfig {A}:0 {B} netmask 255.255.255.0 up");return
			except Exception as F:log(f"Unable to create forward proxy on interface {A}, address {B}: {F}")
	raise Exception('Unable to create network interface')
def run_shell_cmd(command):
	try:return{_D:run_cmd(command)}
	except Exception as A:
		B=str(A)
		if isinstance(A,subprocess.CalledProcessError):B='%s: %s'%(B,A.output)
		return{_B:B}
def get_os():
	if is_mac_os():return'macos'
	if is_linux():return'linux'
	return'windows'
def run_cmd(cmd):log(f"Running command: {cmd}");return to_str(subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=_A))
def log(*A):print(*(A));sys.stdout.flush()
def is_mac_os():
	try:A=to_str(subprocess.check_output(_G,shell=_A));return'Darwin'in A
	except subprocess.CalledProcessError:return False
def is_linux():
	try:A=to_str(subprocess.check_output(_G,shell=_A));return'Linux'in A
	except subprocess.CalledProcessError:return False
def get_ip_address(ifname):import fcntl;A=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);return socket.inet_ntoa(fcntl.ioctl(A.fileno(),35093,struct.pack('256s',to_bytes(ifname[:15])))[20:24])
def get_free_tcp_port():A=socket.socket(socket.AF_INET,socket.SOCK_STREAM);A.bind(('',0));C,B=A.getsockname();A.close();return B
def to_bytes(obj):A=obj;return A.encode('utf-8')if isinstance(A,str)else A
def to_str(obj):A=obj;return A.decode('utf-8')if isinstance(A,bytes)else A
def start_server(port,handler):
	A=port;kill_server(A)
	try:log(f"Starting local daemon server on port {A}");B=ThreadedHTTPServer(('0.0.0.0',A),handler);B.serve_forever()
	except Exception:log(f"Local daemon server already running, or port {A} not available")
def kill_server(port):
	try:requests.post(f"http://localhost:{port}",data='{"op":"kill"}')
	except Exception:pass
def kill_servers():kill_server(DEFAULT_PORT_LOCAL_DAEMON);kill_server(DEFAULT_PORT_LOCAL_DAEMON_ROOT)
def main():
	E='AWS_SECRET_ACCESS_KEY';D='test';C='AWS_ACCESS_KEY_ID';B='main';logging.basicConfig();A=sys.argv[1]if len(sys.argv)>1 else B;os.environ[C]=os.environ.get(C)or D;os.environ[E]=os.environ.get(E)or D
	if A==B:start_server(DEFAULT_PORT_LOCAL_DAEMON,RequestHandler)
	elif A=='root':start_server(DEFAULT_PORT_LOCAL_DAEMON_ROOT,RequestHandlerRoot)
	else:log(f"Unexpected local daemon type: {A}")
def get_log_file_path():from localstack.config import dirs;return os.path.join(dirs.tmp,'localstack_daemon.log')
def start_in_background():
	from localstack.utils.common import run as B;A=get_log_file_path();LOG.info('Logging local daemon output to %s',A);E=sys.executable;C=f"{E} {__file__}";B(C,outfile=A,asynchronous=_A);LOG.info('Attempting to obtain sudo privileges for local daemon of EC2 API (required to start SSH forward proxy on privileged port 22). You may be asked for your sudo password.');B('sudo -v',stdin=_A)
	def F(*E,asynchronous=None):D=f"sudo {C} root >> {A}";B(D,outfile=A,stdin=_A,asynchronous=asynchronous)
	D=FuncThread(F);D.start();return D
if __name__=='__main__':main()