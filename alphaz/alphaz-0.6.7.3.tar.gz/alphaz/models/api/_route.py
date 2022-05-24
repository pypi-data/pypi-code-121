import datetime, os, copy
import traceback
from typing import List, Dict

from flask import (
    Flask,
    jsonify,
    request,
    Response,
    make_response,
    render_template,
    send_from_directory,
)

from ...libs import json_lib, converter_lib, io_lib
from ...models.main import AlphaException
from ...models.api import ApiAnswer, AlphaRequest

from ._parameter import Parameter

SEPARATOR = "__"


def get_columns_values_output(
    objects: list, columns: list = None, header: bool = False
) -> dict:
    """Generate columns names output columns names + list of list (only the values) + nb of values if not header
    ex : { "columns":["col1","col2",...], "values": ["value1","value2",..], "values_nb":12}

    else Generate columns names output columns names + list of JSON objetcs + nb of values,

    ex : { "columns":["col1","col2",...], "values": [{"col1": "value1",...},{...}], "values_nb":12}

    Args:
        objects (list): [description]

    Args:
        objects (list): [description]
        columns (list): [description]
        header (bool): [Add headers to values]

    Returns:
        dict: [description]
    """
    if len(objects) == 0:
        return {"columns": [], "values": [], "values_nb": 0}

    results = json_lib.jsonify_data(objects)

    if columns and len(columns) != 0 and len([x for x in columns if x != ""]) != 0:
        results = [
            {key: value for key, value in result.items() if key in columns}
            for result in results
        ]
    else:
        columns = list(results[0].keys())
    if header:
        return {"columns": columns, "values": results, "values_nb": len(results)}

    data = {}
    data["columns"] = [x for x in columns if x in results[0]]
    data["values"] = [[x[y] for y in columns if y in x] for x in results]
    data["values_nb"] = len(data["values"])
    return data


def check_format(data, depth=3):
    if depth == 0:
        return True

    accepted = [int, str, float]
    if type(data) in accepted:
        return True

    if type(data) == list and len(data) != 0:
        return check_format(data[0], depth - 1)
    if type(data) == dict and len(data) != 0:
        return check_format(list(data.keys())[0], depth - 1) & check_format(
            list(data.values())[0], depth - 1
        )
    return False


class Route():
    no_log = False
    ex = None

    def __init__(
        self,
        uuid: str,
        route: str,
        parameters: List[Parameter],
        request_state,
        cache: bool = False,
        logged: bool = False,
        admin: bool = False,
        timeout=None,
        description: str = "",
        cache_dir=None,
        log=None,
        jwt_secret_key=None,
        mode=None,
    ):
        self.__timeout = timeout
        self.uuid: str = uuid
        self.route: str = route
        self.cache: bool = cache
        self.logged: bool = logged
        self.admin: bool = admin
        self.description = description

        self.full_path = request_state.full_path
        self.files = request.files

        self.args = request_state.args
        self.form = request.form
        self.json = AlphaRequest.get_json()
        self.dict = request.args.to_dict(flat=False)

        self.mode = mode.lower() if mode != None else "data"

        self.lasttime = datetime.datetime.now()

        self.data = {}
        self.returned = {}

        self.html = {"page": None, "parameters": None}
        self.message = "No message"

        self.file_to_get = (None, None)
        self.file_to_set = (None, None)

        self.cache_dir = cache_dir
        self.log = log
        self.method = request_state.method

        self.init_return()

        self.parameters: Dict[Parameter] = {y.name: copy.copy(y) for y in parameters}
        for parameter in self.parameters.values():
            try:
                parameter.set_value(
                    self.method, self.dict, self.json, self.form, self.args
                )
                if parameter.name == "no_log":
                    self.no_log = parameter.value
                else:
                    parameter.no_log = self.no_log
            except Exception as ex:
                # TODO: enhance
                message = traceback.format_exc()
                if isinstance(ex, AlphaException):
                    message = ex.description
                self.set_error(message)
                self.ex = ex
                return

    def is_outdated(self):
        return (datetime.datetime.now() - self.lasttime).total_seconds() > 60 * 5

    def get(self, name, default=None):
        if not name in self.parameters:
            return default

        parameter = self.parameters[name]
        value = None if parameter is None else parameter.value
        if str(value).lower() in ["false", "0", "f"]:
            return False
        if str(value).lower() in ["true", "1", "y"]:
            return True
        return value

    def __getitem__(self, key):
        return self.get(key)

    def is_time(self, timeout):
        is_time = False
        if timeout is not None:
            now = datetime.datetime.now()
            lastrun = self.lasttime
            nextrun = lastrun + datetime.timedelta(minutes=timeout)
            is_time = now > nextrun
        return is_time

    def keep(self):
        if not self.cache:
            return False
        reset_cache = self.get("reset_cache") or self.is_time(self.__timeout)
        if reset_cache:
            return False
        return self.is_cache()

    def get_key(self):
        route = self.route if not self.route[0] == "/" else self.route[1:]
        key = f"{route}__"
        for name, parameter in self.parameters.items():
            if parameter.cacheable and not parameter.private:
                key += f"{parameter.name}-{parameter.value}_"
        return key

    def get_cache_path(self):
        if self.cache_dir is None:
            return None
        key = self.get_key()
        cache_path = self.cache_dir + os.sep + key + ".cache"
        return cache_path

    def is_cache(self):
        cache_path = self.get_cache_path()
        if cache_path is None and not self.no_log:
            self.log.error("Cache path does not exist")
            return False
        return os.path.exists(cache_path)

    def set_cache(self):
        self.lasttime = datetime.datetime.now()
        cache_path = self.get_cache_path()
        if cache_path is None and not self.no_log:
            self.log.error("cache path does not exist")
            return
        try:
            returned = io_lib.archive_object(self.data, cache_path)
        except Exception as ex:
            if not self.no_log:
                self.log.error(f"Cannot cache route {self.get_key()}: {str(ex)}")

    def get_cached(self):
        if self.log and not self.no_log:
            self.log.info(f"GET cache for {self.route}")

        if self.is_cache():
            cache_path = self.get_cache_path()
            data = io_lib.unarchive_object(cache_path)
            if data:
                self.init_return()
                self.set_data(data)
                return True
        return False

    def set_status(self, status):
        self.returned.status = str(status)

    def timeout(self):
        self.returned.status = "timeout"
        self.returned.status_code = 524
        self.returned.error = 1

    def access_denied(self):
        self.returned.status = "unauthorized"
        self.returned.status_description = "unauthorized".capitalize()
        self.returned.token_status = "denied"
        self.returned.error = 1
        self.returned.status_code = 401

    def set_error_not_logged(self):
        self.returned.status = "not_logged"
        self.returned.status_description = "Not logged"
        self.returned.token_status = "denied"
        self.returned.error = 1
        self.returned.status_code = 401

    def set_error(self, message: str, description: str = None):
        if type(message) == AlphaException:
            description = message.description
            message = message.name
            if not self.no_log:
                self.log.error(f"{message} - {description}", level=2)

        self.mode == "data"
        self.returned.status = str(message)
        self.returned.status_code = 520
        self.returned.status_description = str(description if description else message)
        self.returned.error = 1

    def print(self, message):
        self.mode == "print"
        self.message = message

    def init_return(self):
        self.file_to_get = (None, None)
        self.file_to_set = (None, None)
        self.returned, self.data = ApiAnswer(), {}

    def set_data(self, data):
        self.mode == "data"
        self.data = data

    def set_file(self, directory, filename):
        self.mode = "set_file"
        self.file_to_set = (directory, filename)

    def get_file(self, directory, filename, attached=False):
        self.mode = "get_file" if not attached else "get_file_attached"
        self.file_to_get = (directory, filename)

    def set_html(self, page, parameters={}):
        self.mode = "html"
        self.data = {"page": page, "parameters": parameters}

    def get_return(self, forceData=False, return_status=None):
        if self.mode == "html":
            if "page" in self.data:
                return render_template(self.data["page"], **self.data["parameters"])
            else:
                return self.data
        if self.mode == "print":
            return self.message

        if "get_file" in self.route:
            file_path, filename = self.file_to_get
            if file_path is not None and filename is not None:
                if not self.no_log:
                    self.info(f"Sending file {filename} from {file_path}")
                try:
                    return send_from_directory(
                        file_path,
                        filename,
                        as_attachment="attached" in self.mode,
                    )
                except FileNotFoundError:
                    self.set_error("missing_file")
            else:
                self.set_error("missing_file")

        if isinstance(self.data, Exception):
            if hasattr(self.data, "msg"):
                self.set_error(self.data.msg, self.data.msg)
            elif hasattr(self.data, "args"):
                self.set_error(self.data.args[0], self.data.args[0])
            self.data = {}

        self.returned.data = {}

        data = {} if self.data is None else self.data

        # Convert
        self.returned.data = data
        if not check_format(data):
            self.returned.data = json_lib.jsonify_data(data)

        format_ = self.get("format", default="json")
        format_ = format_.lower()

        if "table" in format_:
            self.returned.data = get_columns_values_output(
                self.returned.data, self.get("columns"), header="header" in format_
            )

        if format_ and "xml" in format_:
            xml_output = converter_lib.dict_to_xml(
                self.returned.to_json(), attr_type=not "no_type" in format_
            )
            response = make_response(xml_output)
            response.headers["Content-Type"] = "text/xml; charset=utf-8"
            return response
        else:
            returned = jsonify(self.returned)
            if type(self.returned.status) == int:
                returned.status_code = self.returned.status

        return returned

    def log_user(self, user_data):
        self.returned.role = "user"
        if user_data["role"] >= 9:
            self.returned.role = "admin"
        self.returned.token = jwt.encode(
            {
                "username": user_data["username"],
                "id": user_data["id"],
                "time": str(datetime.datetime.now()),
            },
            self.jwt_secret_key,
            algorithm="HS256",
        ).decode("utf-8")
        self.returned.valid_until = datetime.datetime.now() + datetime.timedelta(days=7)
