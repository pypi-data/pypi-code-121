from typing import List
import uuid

from ...utils.api import route, Parameter, ParameterMode

from .. import tests

from core import core

api         = core.api

@route('/test/cache',cache=True, timeout=100,
    parameters=[
        Parameter("value"), 
        Parameter("options",options=['Y','N'])
    ]
)
def api_test():
    parameters = api.get_parameters()
    parameters['uuid'] = uuid.uuid4()
    return parameters

@route('/test/parameters', methods=["GET","POST"],route_log=False,
    parameters=[
        Parameter("value"), 
        Parameter("options",options=['Y','N',1,2]),
        Parameter("list", ptype=list),
        Parameter("list_str", ptype=List[str]),
        Parameter("list_int", ptype=List[int]),
        Parameter("list_float", ptype=List[float]),
        Parameter("list_default", ptype=list, default=[]),
        Parameter("dict", ptype=dict),
        Parameter("dict_default", ptype=dict, default={}),
        Parameter("string", ptype=str, max_size=100, min_size=5),
        Parameter("string_default", ptype=str,default=""),
        Parameter("integer", ptype=int),
        Parameter("integer_default", ptype=int, default=1),
        Parameter("float", ptype=float),
        Parameter("end_like_mode", ptype=str, mode=ParameterMode.END_LIKE),
        Parameter("in_like_mode", ptype=str, mode=ParameterMode.IN_LIKE),
        Parameter("like_mode", ptype=str, mode=ParameterMode.LIKE),
        Parameter("start_like_mode", ptype=str, mode=ParameterMode.START_LIKE),
        Parameter("none_mode", ptype=str, mode=ParameterMode.NONE),
    ], description="Route used for auto test"
)
def api_test_parameters_route():
    return api.get_parameters()
    
@route('/test/insert',)
def test_insert():
    return tests.insert()

@route('/test/html',
    parameters=[Parameter('message')]
)
def html_message():
    return api.set_html('hello.html',parameters={"message":api.get('message')})


@route("/test/methods", methods=["GET"])
def get_method_1():
    return "GET"


@route("/test/methods", methods=["POST"])
def get_method_2():
    return "POST"


@route("/test/methods", methods=["PUT"])
def get_method_3():
    return "PUT"


@route("/test/methods", methods=["PATCH"])
def get_method_4():
    return "PATCH"


@route("/test/methods", methods=["DELETE"])
def get_method_5():
    return "DELETE"
