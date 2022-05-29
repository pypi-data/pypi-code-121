from operator import mod
import os
from re import S
from sys import argv
from typing import Callable, Dict, List


argsDict = [tuple(a) for a in [a.split('=', maxsplit=1) for a in argv] if len(a) == 2]

context = dict(argsDict)
argsArray = [i.lower() for i in argv if i not in context]


ContextAction = Callable[[Dict[str, str]], int]
ContextActionDecorator = Callable[[ContextAction], ContextAction]

KEY_PROJECT_NAME = 'Project name'
KEY_MAIN_ENDPOINT = 'Main endpoint'
KEY_FOLDER_NAME = 'Folder name'
KEY_MAIN_FILE_NAME = 'Main file'

KEY_STATIC_FILES_FOLDER = 'Static files folder'
KEY_SESSION_KEY = 'Session key'
KEY_TEMP_FILES_FOLDER = 'Temp files folder'
KEY_TEMP_FILES_FOLDER_DURATION = 'Temp files duration (seg)'

PRT_EMPTY = 'empty'
PRT_EXAMPLE = 'example'

if PRT_EMPTY not in argsArray:
    argsArray.append(PRT_EMPTY)


middlewares = {
    "Time measurement": lambda: 'time_measure',
    "Static files serving": lambda: f'static_files("{context[KEY_STATIC_FILES_FOLDER]}")',
    "Authorization control": lambda: 'authorization',
    "Session management": lambda: f'session(Session("{context[KEY_SESSION_KEY]}"))',
    "Multipart form-data parser": lambda: f'multipart_form_data_parser("{context[KEY_TEMP_FILES_FOLDER]}", {context[KEY_TEMP_FILES_FOLDER_DURATION]})',
    "Request body parser": lambda: 'body_parser',
    "Json body parser": lambda: 'json_body_parser',
    "Cors avaliability": lambda: 'cors',
    "Default headers": lambda: 'default_headers(build_default_headers())'
    
}

dataStack:List[str] = []
codeStack:List[ContextAction] = []

executionQueue:List[Callable[[],None]] = []

def enqueue(f:Callable[[],None]):
    global executionQueue
    executionQueue.append(f)

def push_c(funct:ContextAction) -> None:
    codeStack.append(funct)

def pop_c() -> ContextAction:
    return codeStack.pop()
 
def retrieve(key:str):
    context[key] = input(f'{key} :')

def f(name:str, *lines):
    with open(name, 'a', encoding = 'latin1') as fo:
        fo.writelines([i+'\n' for i in lines])

def requires_parameters(params:List[str]) -> ContextActionDecorator:
    def decorator(funct:ContextAction) -> ContextAction:
        def inner(context:Dict[str, str]) -> int:
            for k in params:
                if k not in context:
                    retrieve(k)
            return funct(context)
        return inner
    return decorator

class Templates:
    def __init__(self) -> None:
        pass

    def T0_import_all(module:str) -> str:
        return f'from {module} import *'

    def T1_instance_app(appName:str, port:int = 80) -> str:
        return f'{appName} = Application(get_port({port}))'

    def T2_route(route:str, appName:str = 'app', method:str='get'):
        method = method.lower()
        return '@{0}.{1}("/{2}")'.format(appName, method, route)

    def T3_middleware(functionName:str = 'main'):
        return f'def {functionName}(app:Application, req:HttpRequest, res:HttpResponse):'
    
    def T4_end(text:str='OK', tabLevel:int=1):
        return ("\t"*tabLevel) + f'res.end("{text}")'
        

@requires_parameters([KEY_FOLDER_NAME])
def make_project_folder(context:Dict[str, str]) -> int:
    folderName = context[KEY_FOLDER_NAME]
    def action():
        print(f'creating folder: "{folderName}"')
        try:
            os.mkdir(folderName)
        except Exception as e:
            print(e)
    enqueue(action)
    return 0

@requires_parameters([KEY_FOLDER_NAME, KEY_MAIN_FILE_NAME])
def create_main_file(context:Dict[str, str]) -> int:
    fileName = os.sep.join([context[KEY_FOLDER_NAME], context[KEY_MAIN_FILE_NAME]])
    def action():
        print(f'creating file: "{fileName}"')
        f(fileName, Templates.T0_import_all('threadsnake.core'))
        f(fileName, Templates.T1_instance_app('app', 80))
    enqueue(action)
    return 0

@requires_parameters([KEY_MAIN_ENDPOINT, KEY_MAIN_FILE_NAME])
def create_main_endpoint(context:Dict[str, str]) -> int:
    fileName = os.sep.join([context[KEY_FOLDER_NAME], context[KEY_MAIN_FILE_NAME]])
    endpoint = context[KEY_MAIN_ENDPOINT]
    def action():
        print(f'creating main endpoint "{endpoint}" in file: "{fileName}"')
        f(fileName, Templates.T2_route(endpoint, 'app', 'get'))
        f(fileName, Templates.T3_middleware('main'))
        f(fileName, Templates.T4_end('OK'))
    enqueue(action)
    return 0

templates = {
    PRT_EMPTY:[make_project_folder, create_main_file, create_main_endpoint]
}

for k in templates:
    if k in argsArray:
        for funct in templates[k]:
            push_c(funct)
        codeStack.reverse()
        while len(codeStack) > 0:
            if (pop_c())(context) != 0:
                break
        for e in executionQueue:
            e()