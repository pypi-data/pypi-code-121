
import datetime, glob, os, re, platform, requests

from flask import request, send_from_directory

from ...libs import test_lib, database_lib, api_lib, transactions_lib, py_lib
from ...utils.api import route, Parameter
from ...utils.time import tic, tac
from ...models.main import AlphaException

from core import core

api = core.api
db = core.db

LOG = core.get_logger("logs")

CLUSTERS = core.config.get('clusters')

def escape_ansi(line):
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', str(line))

def get_logs_files_names():
    log_directory = core.config.get('directories/logs')
    files = glob.glob(log_directory + os.sep + '*.log')
    return [os.path.basename(x) for x in files]

def log_a_message(logger:str, criticality:str, message:str, level:int, monitor:str=None):
    log = core.get_logger(logger)
    if log is None:
        raise AlphaException(f"No {logger=} found")
    if hasattr(log, criticality):
        getattr(log, criticality)(message=message, monitor=monitor, level=level)
        return True 
    return False

def get_logs_content(name:str=None, node:str=None, content:bool=False, single:bool=False): 
    current_node = platform.uname().node
    if node is not None and node.lower() != current_node.lower():
        url = f'http://{node}:{api.port}/logs/files'

        params = api.get_parameters()
        params['cluster'] = False

        resp = requests.get(url=url, params=params)
        if resp.status_code == 200:
            data = resp.json()
            if data['error'] == 0:
                return data['data']
        return {}

    log_directory = core.config.get('directories/logs')
    separator = "-"
    if not single:
        path_pattern = log_directory + os.sep + (name if name is not None else "") + '*.log*'
    else:
        path_pattern = log_directory + os.sep + (name.replace(separator,'.log.') if separator in name else name+ ".log")
    files = glob.glob(path_pattern)

    logs_content = {}
    for file_path in files:
        modification_time = os.path.getmtime(file_path)
        modification_date = datetime.datetime.fromtimestamp(int(modification_time))

        name = os.path.basename(file_path)

        log_content = ""
        if content:
            with open(file_path,'r') as f:
                log_content = f.read()
        #log_content = escape_ansi(log_content)

        file_size = os.path.getsize(file_path)
        name = name.replace('.log','')
        name = name.replace('.',separator)

        logs_content[name + separator + platform.uname().node] = {
            "name": name,
            "node": platform.uname().node,
            "modification_time":modification_time,
            "modification_date":modification_date,
            "up_to_date": modification_date.date() == datetime.datetime.today().date(),
            "size": file_size,
            "size_s": "%s b"%file_size if file_size < 100 else "%s Kb"%int(file_size/1000),
            "content": log_content
        } 
    logs_content = {k: v for k, v in sorted(logs_content.items(), key=lambda item: item[1]['modification_time'],reverse=True)}
    return logs_content

def get_log_content(name:str, content:bool=False):
    return get_logs_content(name, content)[name]

def get_logs_content_cluster(name:str=None, node:str=None, content:bool=False):
    os_logs_content = get_logs_content(api['name'], node=node, content=api['content'])

    in_cluster = []
    if CLUSTERS is not None and type(CLUSTERS) is list and node is None:
        for clusters in CLUSTERS:
            if type(clusters) is not list or not platform.uname().node.lower() in [x.lower() for x in clusters]:
                continue

            for cluster in clusters:
                if platform.uname().node.lower() == cluster.lower():
                    continue
                in_cluster.append(cluster.lower())
                url = 'http://%s:%s/logs/files'%(cluster.lower(), api.port)

                params = api.get_parameters()
                params['cluster'] = False

                try:
                    resp = requests.get(url=url, params=params)
                except Exception as ex:
                    LOG.error(f'Fail to contact {url}', ex=ex)
                    continue

                if resp.status_code == 200:
                    data = resp.json()
                    if data['error'] == 0:
                        for key, cf in data['data'].items():
                            os_logs_content[key] = cf
    LOG.info("%s logs files found in cluster: %s, %s"%(len(os_logs_content),platform.uname().node.lower(), ", ".join(in_cluster)))
    os_logs_content = {k: v for k, v in sorted(os_logs_content.items(), key=lambda item: item[1]['modification_time'],reverse=True)}
    return os_logs_content

@route("/log", route_log=False, parameters=[
    Parameter("logger", default="main"),
    Parameter("criticality", default="info", options=["debug","info","warning","error","critical"],function=str.lower),
    Parameter("message"),
    Parameter("level", ptype=int, default=1),
    Parameter("monitor", default=None)
], description="Log a message")
def log_a_message_route():
    return log_a_message(**api.get_parameters())

@route("/logs/filesnames", methods=['GET'], route_log=False, parameters=[])
def get_logs():
    return get_logs_files_names()

@route("/logs/files", methods=['GET'], route_log=False, parameters=[
    Parameter('name'),
    Parameter('node'),
    Parameter('content', ptype=bool, default=False),
    Parameter('cluster', ptype=bool, default=True),
])
def get_logs_file_content():
    if api['cluster']:
        return get_logs_content_cluster(api['name'], node=api['node'], content=api['content'])
    return get_logs_content(api['name'], node=api['node'], content=api['content'])

@route("/logs/file", methods=['GET'], route_log=False, parameters=[
    Parameter('name'),
    Parameter('node'),
    Parameter('content', ptype=bool, default=False)
])
def get_log_file_content():
    logs_dict = get_logs_content(api['name'], node=api['node'], content=api['content'], single=True)
    if len(logs_dict) == 0:
        return logs_dict
    return logs_dict[list(logs_dict.keys())[0]]

@route("/logs")
def get_logs_page():
    config = api.conf

    parameters = {
        "mode": core.config.configuration,
        "mode_color": "#e74c3c"
        if core.config.configuration == "prod"
        else ("#0270D7" if core.config.configuration == "dev" else "#2ecc71"),
        "title": config.get("templates/home/title"),
        "description": config.get("templates/home/description"),
        "year": datetime.datetime.now().year,
        "users": 0,
        "ip": request.environ["REMOTE_ADDR"],
        "admin": config.get("admin_databases"),
        "compagny": config.get("parameters/compagny"),
        "compagny_website": config.get("parameters/compagny_website"),
        "dashboard": config.get("dashboard/dashboard/active"),
        "date": datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "logs_files": get_logs_content_cluster(content=False)
    }
    api.set_html("logs.html", parameters=parameters)