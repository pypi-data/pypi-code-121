import os, socket, logging, base64, re
import urllib.request
from getpass import getpass
from urllib.parse import unquote, urlparse
from contextlib import closing
from zut.credentials import get_password, set_password

def check_socket(host, port, timeout=1):
    logger = logging.getLogger(__name__)

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        try:
            returncode = sock.connect_ex((host, port))
            if returncode == 0:
                return True
            else:
                logger.debug("socket connnect_ex returned %d", returncode)
                return False
        except Exception as e:
            logger.debug("socket connnect_ex: %s", e)
            return False


class SimpleProxyHandler(urllib.request.BaseHandler):
    # Inspired from urllib.request.ProxyHandler   
    handler_order = 100 # Proxies must be in front

    def __init__(self, host: str, port: str, username: str = None, password: str = None, scheme: str = "http"):
        self.proxy_hostport = unquote(f"{host}:{port}")
        self.proxy_type = scheme

        if username:
            userpass = '%s:%s' % (unquote(username), unquote(password))
            self.proxy_authorization = "Basic " + base64.b64encode(userpass.encode()).decode("ascii")
        else:
            self.proxy_authorization = None


    def http_open(self, req):
        if not req.host:
            return None
        
        if urllib.request.proxy_bypass(req.host):
            # NOTE: because Proxy-Authorization header is not encrypted, we must add it ONLY when we're actually talking to the proxy
            return None

        if self.proxy_authorization:
            req.add_header("Proxy-Authorization", self.proxy_authorization)
        req.set_proxy(self.proxy_hostport, self.proxy_type)
        return None
    
    def https_open(self, req):
        return self.http_open(req)


def register_urllib_proxy(proxy_url:str=None, proxy_exclusions:str=None, prompt_password=False):
    logger = logging.getLogger(__name__)

    if not proxy_url:
        if "HTTP_PROXY" in os.environ:
            proxy_url = os.environ["HTTP_PROXY"]
        elif "http_proxy" in os.environ:
            proxy_url = os.environ["http_proxy"]

    if not proxy_url:
        return

    if not proxy_exclusions:
        if "NO_PROXY" in os.environ:
            proxy_exclusions = os.environ["NO_PROXY"]
        elif "no_proxy" in os.environ:
            proxy_exclusions = os.environ["no_proxy"]

    if isinstance(proxy_exclusions, list):
        proxy_exclusions = ",".join(proxy_exclusions)

    # Parse proxy URL
    o = urlparse(proxy_url)
    m = re.match(r"^(?:(?P<username>[^\:]+)(?:\:(?P<password>[^\:]+))?@)?(?P<host>[^@\:]+)\:(?P<port>\d+)$", o.netloc)
    if not m:
        logger.error("cannot register proxy: invalid proxy netloc \"%s\"" % o.netloc)
        return

    proxy_host = m.group("host")
    proxy_port = int(m.group("port"))
    proxy_username = m.group("username")
    proxy_password = m.group("password")
    proxy_scheme = o.scheme

    # Check proxy existency
    if not check_socket(proxy_host, proxy_port):
        logger.warning(f"cannot connect to proxy {proxy_host}:{proxy_port}")

    # Search password in system credentials
    if proxy_username and not proxy_password:
        preferred_service_name = "git:http://" + proxy_host  # for mutualization with Git
        proxy_password = get_password(preferred_service_name, proxy_username)
        if proxy_password is None:
            proxy_password = get_password(proxy_host, proxy_username)
        if proxy_password is None:
            if prompt_password:
                proxy_password = getpass(f"Please provide password for \"{proxy_host}\" (username \"{proxy_username}\")")
                set_password(preferred_service_name, proxy_username, proxy_password)
            else:
                logger.error(f"cannot register proxy: no password found for \"{proxy_host}\" (username \"{proxy_username}\")")
                return

    # Ensure no_proxy is specified (must be passed as environment variable for urllib)
    os.environ["no_proxy"] = proxy_exclusions

    # Register proxy for urllib
    try:
        proxy_handler = SimpleProxyHandler(host=proxy_host, port=proxy_port, username=proxy_username, password=proxy_password, scheme=proxy_scheme)
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
    except Exception as e:
        logger.error("cannot register proxy: %s", e)
