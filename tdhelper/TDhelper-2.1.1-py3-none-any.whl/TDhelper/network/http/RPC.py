import json
import copy
import random
from typing import List, Tuple, Dict
from urllib import parse
from types import FunctionType
from TDhelper.generic.classDocCfg import doc
from network.http.REST_HTTP import GET, POST,PUT,DELETE,ContentType
from TDhelper.Decorators.log import logging, logging_setup
from TDhelper.generic.randGetValue import getValue

## 以后整理。测试用
class RPCRegister:
    def __init__(self, serviceConfig, HostConfig, rpcConfig):
        self._serviceConfig = serviceConfig
        self._hostConfig = HostConfig
        self._access_token = rpcConfig["token"]
        self._m_heads = {}
        self._m_heads["api-token"] = self._access_token if self._access_token else ""
        # rpc uri传数组过来，从数组里随机取一个服务地址。后续需要做负载均衡。
        self._sc_uri = getValue(rpcConfig["uri"]).strip("/") + "/"

    def RegisterRPC(self):
        return self._registerService()

    def RegisterMethod(self, pk, serviceClass):
        self._registerMehotd(pk, serviceClass)

    def _registerService(self):
        m_service_post_data = ""
        m_count = 0
        # 生成注册服务参数.
        for k, v in self._serviceConfig.items():
            if k.lower() != "description":
                if not v:
                    raise Exception("service '%s' value can't is none." % k)
            m_service_post_data += k + "=" + parse.quote(str(v))
            m_count += 1
            if m_count < len(self._serviceConfig):
                m_service_post_data += "&"
        # 注册服务基本信息.
        state, ret = POST(
            self._sc_uri + "services/".strip("/") + "/",
            post_data=bytes(m_service_post_data, encoding="utf-8"),
            http_headers=self._m_heads,
            time_out=15,
        )
        if state == 200:
            ret = str(ret, encoding="utf-8")
            ret = json.loads(ret, encoding="utf-8")
            if ret["state"] == 200:
                logging.info(
                    "%s(%s) register success."
                    % (self._serviceConfig["key"], self._serviceConfig["name"])
                )
                if ret["msg"]["id"]:
                    self._registerHost(ret["msg"]["id"], self._hostConfig)
                    # self._registerMehotd(ret["msg"]["id"], serviceClass)
                    return ret["msg"]["id"]
                else:
                    return None
            else:
                return None
        else:
            return None

    def _registerHost(self, pk, hosts):
        # 注册服务器信息.
        for i in range(0, len(hosts)):
            hosts[i]["service"] = pk
            hosts[i]["state"] = True
            m_count = 0
            m_service_hosts_post_data = ""
            for k, v in hosts[i].items():
                if v:
                    m_service_hosts_post_data += k + "=" + parse.quote(str(v))
                    m_count += 1
                    if m_count < len(hosts[i]):
                        m_service_hosts_post_data += "&"
                else:
                    raise Exception("register hosts {} can't is none." % k)
            state, ret = POST(
                self._sc_uri + "hosts/".strip("/") + "/",
                post_data=bytes(m_service_hosts_post_data, encoding="utf-8"),
                http_headers=self._m_heads,
                time_out=15,
            )
            if state != 200:
                logging.error(
                    "register service hosts failed. msg:{}" % str(ret, encoding="utf-8")
                )
            else:
                ret = json.loads(str(ret, encoding="utf-8"))
                if ret["state"] != 200:
                    m_msg = "register service hosts failed. http code({}), msg:{}" % (
                        ret["state"],
                        ret["msg"],
                    )
                    logging.error(m_msg)
                else:
                    logging.info(
                        "register service hosts(%s:%s) success."
                        % (hosts[i]["host"], hosts[i]["port"])
                    )

    def _registerMehotd(self, pk, serviceClass):
        # 注册方法
        for k, v in serviceClass.__dict__.items():
            if isinstance(v, FunctionType):
                func_name = v.__name__.upper()
                if v.__doc__:
                    methods = doc(v.__doc__, "rpc")
                    if methods:
                        methods = methods.replace("\n", "").strip()
                        try:
                            methods = [json.loads(methods, encoding="utf-8")]
                            for i in range(0, len(methods)):
                                # todo register method.
                                methods[i]["service"] = pk
                                if not "key" in methods[i]:
                                    methods[i]["key"] = (
                                        self._serviceConfig["key"].upper()
                                        + "."
                                        + serviceClass.__name__.upper()
                                        + "_"
                                        + func_name
                                    )
                                else:
                                    if not methods[i]["key"]:
                                        methods[i]["key"] = (
                                            self._serviceConfig["key"].upper()
                                            + "."
                                            + serviceClass.__name__.upper()
                                            + "_"
                                            + func_name
                                        )
                                    else:
                                        if len(methods[i]["key"].split(".")) == 1:
                                            methods[i]["key"] = (
                                                self._serviceConfig["key"].upper()
                                                + "."
                                                + serviceClass.__name__.upper()
                                                + "_"
                                                + methods[i]["key"]
                                            )
                                        else:
                                            logging.error(
                                                "%s key can not contain (.) ."
                                                % methods[i]["key"]
                                            )
                                m_service_uri_post_data = ""
                                if not methods[i]["uri"].endswith("/"):
                                    methods[i]["uri"] += "/"
                                m_count = 0
                                for k, v in methods[i].items():
                                    if k.lower() != "params":
                                        if (
                                            k.lower() == "key"
                                            or k.lower() == "uri"
                                            or k.lower() == "method"
                                        ):
                                            if not v:
                                                raise Exception(
                                                    "methods (%s) is none." % k.lower()
                                                )
                                        if k.lower() != "method":
                                            m_service_uri_post_data += (
                                                k + "=" + parse.quote(str(v))
                                            )
                                        else:
                                            m_value = 0
                                            if v.upper() == u"GET":
                                                m_value = 1
                                            elif v.upper() == u"POST":
                                                m_value = 2
                                            elif v.upper() == u"PUT":
                                                m_value = 3
                                            elif v.upper() == u"DELETE":
                                                m_value = 4
                                            m_service_uri_post_data += (
                                                k + "=" + str(m_value)
                                            )
                                        m_count += 1
                                        if "params" in methods[i]:
                                            if m_count < len(methods[i]) - 1:
                                                m_service_uri_post_data += "&"
                                        else:
                                            if m_count < len(methods[i]):
                                                m_service_uri_post_data += "&"
                                state, ret = POST(
                                    self._sc_uri + "uri/".strip("/") + "/",
                                    post_data=bytes(
                                        m_service_uri_post_data, encoding="utf8"
                                    ),
                                    http_headers=self._m_heads,
                                    time_out=15,
                                )
                                if state != 200:
                                    logging.error(
                                        "register service methods failed. msg:{}"
                                        % str(ret, encoding="utf-8")
                                    )
                                else:
                                    ret = json.loads(str(ret, encoding="utf-8"))
                                    if ret["state"] != 200:
                                        m_msg = (
                                            "register service methods failed. http code(%d), msg:%s"
                                            % (ret["state"], ret["msg"])
                                        )
                                        logging.error(m_msg)
                                    else:
                                        logging.info(
                                            "%s register success." % methods[i]["key"]
                                        )
                                        if ret:
                                            if "params" in methods[i]:
                                                params = methods[i]["params"]
                                                m_method_id = ret["msg"]["id"]
                                                if params:
                                                    # 有参数能注册.
                                                    for param_offset in range(
                                                        0, len(params)
                                                    ):
                                                        params[param_offset][
                                                            "serviceUri"
                                                        ] = m_method_id
                                                        m_service_method_params_post_data = (
                                                            ""
                                                        )
                                                        m_count = 0
                                                        for k, v in params[
                                                            param_offset
                                                        ].items():
                                                            if not v:
                                                                raise Exception(
                                                                    "methods params (%s) is none."
                                                                    % k.lower()
                                                                )
                                                            m_service_method_params_post_data += (
                                                                k
                                                                + "="
                                                                + parse.quote(str(v))
                                                            )
                                                            m_count += 1
                                                            try:
                                                                if m_count < len(
                                                                    params[param_offset]
                                                                ):
                                                                    m_service_method_params_post_data += (
                                                                        "&"
                                                                    )
                                                            except Exception as e:
                                                                raise e
                                                        state, ret = POST(
                                                            self._sc_uri
                                                            + "params/".strip("/")
                                                            + "/",
                                                            post_data=bytes(
                                                                m_service_method_params_post_data,
                                                                encoding="utf-8",
                                                            ),
                                                            http_headers=self._m_heads,
                                                            time_out=15,
                                                        )
                                            # 注册返回值
                                            if "returns" in methods[i]:
                                                m_returns = methods[i]["returns"]
                                                if m_returns:
                                                    # 有返回值设置进行注册.
                                                    reg_returns_params = ""
                                                    m_count = 0
                                                    m_returns[
                                                        "serviceUri"
                                                    ] = m_method_id
                                                    for k, v in m_returns.items():
                                                        if k.lower() != "descriptions":
                                                            reg_returns_params += (
                                                                k
                                                                + "="
                                                                + parse.quote(str(v))
                                                            )
                                                            m_count += 1
                                                            if (
                                                                "descriptions"
                                                                in m_returns
                                                            ):
                                                                if (
                                                                    m_count
                                                                    < len(m_returns) - 1
                                                                ):
                                                                    reg_returns_params += (
                                                                        "&"
                                                                    )
                                                            else:
                                                                if m_count < len(
                                                                    m_returns
                                                                ):
                                                                    reg_returns_params += (
                                                                        "&"
                                                                    )
                                                    state, ret = POST(
                                                        self._sc_uri
                                                        + "returns/".strip("/")
                                                        + "/",
                                                        post_data=bytes(
                                                            reg_returns_params,
                                                            encoding="utf-8",
                                                        ),
                                                        http_headers=self._m_heads,
                                                        time_out=15,
                                                    )
                                                    if state == 200:
                                                        ret = json.loads(
                                                            str(ret, encoding="utf-8")
                                                        )
                                                        if ret["state"] != 200:
                                                            m_msg = "register service methods failed. http code(%d), msg:%s" % (
                                                                ret["state"],
                                                                ret["msg"],
                                                            )
                                                            logging.error(m_msg)
                                                        else:
                                                            m_returns_id = ret["msg"][
                                                                "id"
                                                            ]
                                                            if (
                                                                "descriptions"
                                                                in m_returns
                                                            ):
                                                                # 注册返回值说明
                                                                for item in m_returns[
                                                                    "descriptions"
                                                                ]:
                                                                    m_returns_description = (
                                                                        "returns="
                                                                        + str(
                                                                            m_returns_id
                                                                        )
                                                                    )
                                                                    m_returns_description += (
                                                                        "&key="
                                                                        + parse.quote(
                                                                            item["key"]
                                                                        )
                                                                    )
                                                                    m_description = item[
                                                                        "valueDescription"
                                                                    ]
                                                                    m_description = m_description.replace(
                                                                        "<", "&lt;"
                                                                    )
                                                                    m_description = m_description.replace(
                                                                        ">", "&gt;"
                                                                    )
                                                                    m_description = m_description.replace(
                                                                        "\r\n", "<br />"
                                                                    )
                                                                    m_returns_description += (
                                                                        "&valueDescription="
                                                                        + parse.quote(
                                                                            m_description
                                                                        )
                                                                    )
                                                                    state, ret = POST(
                                                                        self._sc_uri
                                                                        + "returnDescriptons/".strip(
                                                                            "/"
                                                                        )
                                                                        + "/",
                                                                        post_data=bytes(
                                                                            m_returns_description,
                                                                            encoding="utf-8",
                                                                        ),
                                                                        http_headers=self._m_heads,
                                                                        time_out=15,
                                                                    )
                                                                    if state != 200:
                                                                        m_msg = (
                                                                            "register return description failed. http code(%d)"
                                                                            % state
                                                                        )
                                                                        logging.error(
                                                                            m_msg
                                                                        )
                                                                    else:
                                                                        ret = json.loads(
                                                                            str(
                                                                                ret,
                                                                                encoding="utf-8",
                                                                            )
                                                                        )
                                                                        if (
                                                                            ret["state"]
                                                                            != 200
                                                                        ):
                                                                            m_msg = "register return description failed. state(%d), msg(%s), key()" % (
                                                                                ret[
                                                                                    "state"
                                                                                ],
                                                                                ret[
                                                                                    "msg"
                                                                                ],
                                                                                item[
                                                                                    "key"
                                                                                ],
                                                                            )
                                                                            logging.error(
                                                                                m_msg
                                                                            )
                                                    else:
                                                        m_msg = (
                                                            "register returns failed. http code(%d)"
                                                            % state
                                                        )
                                                        logging.error(m_msg)

                                        else:
                                            if ret["state"] != 200:
                                                m_msg = (
                                                    "register service hosts failed. http code(%d), msg:%s"
                                                    % (ret["state"], ret["msg"])
                                                )
                                                logging.error(m_msg)
                        except Exception as e:
                            logging.error(e)
                            logging.error(
                                "register params error. method config error.please checked %s.__doc__"
                                % (v.__name__)
                            )


class RPC:
    """
    RPC. 此类只能配合webservice/rpc使用, 独立使用将会报错.
    """

    def __init__(self, service_center_uri, secret):
        """
        初始化
        - params:
        -   service_center_uri:<string>, 服务中心获取API接口URI.
        -   secret: <string>, 访问密钥
        """
        self._access_token = secret
        self._m_heads = {}
        self._m_heads["api-token"] = self._access_token if self._access_token else ""
        self._sc_uri = getValue(service_center_uri).rstrip("/") + "/"
        self._apisTable = {}
        self._current_service = None

    def RPC_ACCESS(
        self,
        entryPoint: List[str],
        access_token: str,
        method: str,
        **kwargs: "dict|Tuple"
    ):
        method = parse.quote(method)
        params = ""
        headers = {}
        if "headers" in kwargs:
            headers = kwargs["headers"]
        headers["api-token"] = access_token
        for o in kwargs:
            if o.lower() != "headers":
                params += o + "=" + kwargs[o]
        params = "?" + params
        result = {"state": False, "msg": ""}
        for uri in entryPoint:
            uri = uri.rstrip("/") + "/" + method.strip("/") + "/" + params
            status, body = GET(uri=uri, time_out=15, http_headers=headers)
            if status == 200:
                body = json.loads(str(body, encoding="utf-8"))
                if body["state"] == 200:
                    result["state"] = True
                    result["msg"] = body["msg"]
                break
        return result["state"], result["msg"]

    def _getApi(self, service, method):
        if service + method not in self._apisTable:
            # 远程获取
            method = parse.quote(method)
            status, body = GET(
                uri=self._sc_uri + "rpc/?key=" + service + "&method=" + method,
                time_out=15,
                http_headers=self._m_heads,
            )
            if status == 200:
                self._apisTable[service + method] = json.loads(
                    str(body, encoding="utf-8")
                )
        # 从本地获取API配置
        if service + method in self._apisTable:
            if self._apisTable[service + method]["state"] == 200:
                return True, self._apisTable[service + method]["msg"]
            else:
                return False, self._apisTable[service + method]["msg"]
        else:
            return False, "can't found %s api." % service + method

    def register(self, service: Dict, hosts: List, methods: List) -> Tuple:
        """
        注册服务
        - params:
        -   service: <dict>, 服务信息. formatter:{"name":"","description":"","key":"","httpProtocol":""}
        -   hosts: <[]>, 服务器信息. formatter:[{"host":"ip地址","port":端口}]
        -   methods: <[]>, 方法. formatter: [{"key":"方法索引","uri":"api url","method":"GET|POST|PUT|DELETE","version":"版本号","description":"描述", "params":[{"key":"参数名称","description":"描述","defaultValue":"默认值(调用不传参时默认值)"}],"returns":[{"valueType":"json|xml","examples":"html code","descriptions":[{"key":"值key","valueDescription":"值描述"}]}]}]
        - Returns:
        -   bool, str: 状态，信息.
        """
        m_service_post_data = ""
        m_count = 0
        # 生成注册服务参数.
        for k, v in service.items():
            if k.lower() != "description":
                if not v:
                    raise Exception("service '%s' value can't is none." % k)
            m_service_post_data += k + "=" + parse.quote(str(v))
            m_count += 1
            if m_count < len(service):
                m_service_post_data += "&"
        # 注册服务基本信息.
        state, ret = POST(
            self._sc_uri + "services/",
            post_data=bytes(m_service_post_data, encoding="utf-8"),
            http_headers=self._m_heads,
            time_out=15,
        )
        if state == 200:
            if ret:
                ret = json.loads(str(ret, encoding="utf-8"))
                if ret["state"] == 200:
                    m_service_id = ret["msg"]["id"]
                    # 注册服务器信息.
                    for i in range(0, len(hosts)):
                        hosts[i]["service"] = m_service_id
                        # hosts[i]['state']= True
                        m_count = 0
                        m_service_hosts_post_data = ""
                        for k, v in hosts[i].items():
                            if v:
                                m_service_hosts_post_data += (
                                    k + "=" + parse.quote(str(v))
                                )
                                m_count += 1
                                if m_count < len(hosts[i]):
                                    m_service_hosts_post_data += "&"
                            else:
                                raise Exception("register hosts {} can't is none." % k)
                        state, ret = POST(
                            self._sc_uri + "hosts/",
                            post_data=bytes(
                                m_service_hosts_post_data, encoding="utf-8"
                            ),
                            http_headers=self._m_heads,
                            time_out=15,
                        )
                        if state != 200:
                            return False, "register service hosts failed. msg:{}" % str(
                                ret, encoding="utf-8"
                            )
                        else:
                            ret = json.loads(str(ret, encoding="utf-8"))
                            if ret["state"] != 200:
                                m_msg = (
                                    "register service hosts failed. http code({}), msg:{}"
                                    % (ret["state"], ret["msg"])
                                )
                                return False, m_msg
                    # 注册方法
                    for i in range(0, len(methods)):
                        # todo register method.
                        methods[i]["service"] = m_service_id
                        m_service_uri_post_data = ""
                        m_count = 0
                        for k, v in methods[i].items():
                            if k.lower() != "params":
                                if (
                                    k.lower() == "key"
                                    or k.lower() == "uri"
                                    or k.lower() == "method"
                                ):
                                    if not v:
                                        raise Exception(
                                            "methods (%s) is none." % k.lower()
                                        )
                                if k.lower() != "method":
                                    m_service_uri_post_data += (
                                        k + "=" + parse.quote(str(v))
                                    )
                                else:
                                    m_value = 0
                                    if v.upper() == u"GET":
                                        m_value = 1
                                    elif v.upper() == u"POST":
                                        m_value = 2
                                    elif v.upper() == u"PUT":
                                        m_value = 3
                                    elif v.upper() == u"DELETE":
                                        m_value = 4
                                    m_service_uri_post_data += k + "=" + str(m_value)
                                m_count += 1
                                if "params" in methods[i]:
                                    if m_count < len(methods[i]) - 1:
                                        m_service_uri_post_data += "&"
                                else:
                                    if m_count < len(methods[i]):
                                        m_service_uri_post_data += "&"
                        state, ret = POST(
                            self._sc_uri + "uri/",
                            post_data=bytes(m_service_uri_post_data, encoding="utf8"),
                            http_headers=self._m_heads,
                            time_out=15,
                        )
                        if state != 200:
                            return (
                                False,
                                "register service methods failed. msg:{}"
                                % str(ret, encoding="utf-8"),
                            )
                        else:
                            ret = json.loads(str(ret, encoding="utf-8"))
                            if ret["state"] != 200:
                                m_msg = (
                                    "register service methods failed. http code(%d), msg:%s"
                                    % (ret["state"], ret["msg"])
                                )
                                return False, m_msg
                            else:
                                if ret:
                                    if "params" in methods[i]:
                                        params = methods[i]["params"]
                                        m_method_id = ret["msg"]["id"]
                                        if params:
                                            # 有参数能注册.
                                            for param_offset in range(0, len(params)):
                                                params[param_offset][
                                                    "serviceUri"
                                                ] = m_method_id
                                                m_service_method_params_post_data = ""
                                                m_count = 0
                                                for k, v in params[
                                                    param_offset
                                                ].items():
                                                    if not v:
                                                        raise Exception(
                                                            "methods params (%s) is none."
                                                            % k.lower()
                                                        )
                                                    m_service_method_params_post_data += (
                                                        k + "=" + parse.quote(str(v))
                                                    )
                                                    m_count += 1
                                                    try:
                                                        if m_count < len(
                                                            params[param_offset]
                                                        ):
                                                            m_service_method_params_post_data += (
                                                                "&"
                                                            )
                                                    except Exception as e:
                                                        raise e
                                                state, ret = POST(
                                                    self._sc_uri + "params/",
                                                    post_data=bytes(
                                                        m_service_method_params_post_data,
                                                        encoding="utf-8",
                                                    ),
                                                    http_headers=self._m_heads,
                                                    time_out=15,
                                                )
                                    # 注册返回值
                                    if "returns" in methods[i]:
                                        m_returns = methods[i]["returns"]
                                        if m_returns:
                                            # 有返回值设置进行注册.
                                            reg_returns_params = ""
                                            m_count = 0
                                            m_returns["serviceUri"] = m_method_id
                                            for k, v in m_returns.items():
                                                if k.lower() != "descriptions":
                                                    reg_returns_params += (
                                                        k + "=" + parse.quote(str(v))
                                                    )
                                                    m_count += 1
                                                    if "descriptions" in m_returns:
                                                        if m_count < len(m_returns) - 1:
                                                            reg_returns_params += "&"
                                                    else:
                                                        if m_count < len(m_returns):
                                                            reg_returns_params += "&"
                                            state, ret = POST(
                                                self._sc_uri + "returns/",
                                                post_data=bytes(
                                                    reg_returns_params, encoding="utf-8"
                                                ),
                                                http_headers=self._m_heads,
                                                time_out=15,
                                            )
                                            if state == 200:
                                                ret = json.loads(
                                                    str(ret, encoding="utf-8")
                                                )
                                                if ret["state"] != 200:
                                                    m_msg = (
                                                        "register service methods failed. http code(%d), msg:%s"
                                                        % (ret["state"], ret["msg"])
                                                    )
                                                    return False, m_msg
                                                else:
                                                    m_returns_id = ret["msg"]["id"]
                                                    if "descriptions" in m_returns:
                                                        # 注册返回值说明
                                                        for item in m_returns[
                                                            "descriptions"
                                                        ]:
                                                            m_returns_description = (
                                                                "returns="
                                                                + str(m_returns_id)
                                                            )
                                                            m_returns_description += (
                                                                "&key="
                                                                + parse.quote(
                                                                    item["key"]
                                                                )
                                                            )
                                                            m_description = item[
                                                                "valueDescription"
                                                            ]
                                                            m_description = (
                                                                m_description.replace(
                                                                    "<", "&lt;"
                                                                )
                                                            )
                                                            m_description = (
                                                                m_description.replace(
                                                                    ">", "&gt;"
                                                                )
                                                            )
                                                            m_description = (
                                                                m_description.replace(
                                                                    "\r\n", "<br />"
                                                                )
                                                            )
                                                            m_returns_description += (
                                                                "&valueDescription="
                                                                + parse.quote(
                                                                    m_description
                                                                )
                                                            )
                                                            state, ret = POST(
                                                                self._sc_uri
                                                                + "returnDescriptons/",
                                                                post_data=bytes(
                                                                    m_returns_description,
                                                                    encoding="utf-8",
                                                                ),
                                                                http_headers=self._m_heads,
                                                                time_out=15,
                                                            )
                                                            if state != 200:
                                                                m_msg = (
                                                                    "register return description failed. http code(%d)"
                                                                    % state
                                                                )
                                                                return False, m_msg
                                                            else:
                                                                ret = json.loads(
                                                                    str(
                                                                        ret,
                                                                        encoding="utf-8",
                                                                    )
                                                                )
                                                                if ret["state"] != 200:
                                                                    m_msg = "register return description failed. state(%d), msg(%s), key()" % (
                                                                        ret["state"],
                                                                        ret["msg"],
                                                                        item["key"],
                                                                    )
                                                                    return False, m_msg
                                            else:
                                                m_msg = (
                                                    "register returns failed. http code(%d)"
                                                    % state
                                                )
                                                return False, m_msg

                                else:
                                    if ret["state"] != 200:
                                        m_msg = (
                                            "register service hosts failed. http code(%d), msg:%s"
                                            % (ret["state"], ret["msg"])
                                        )
                                        return False, m_msg
                    return True, "register service success."
                else:
                    msg = "register service http error. http code(%s), msg:%s" % (
                        ret["state"],
                        ret["msg"],
                    )
                    return False, msg
            else:
                raise Exception("register return body is none, please checked.")
        else:
            msg = "register service http error. http code(%d), msg:%s" % (
                state,
                str(ret, encoding="utf-8"),
            )
            return False, msg

    def handle(self, service):
        """
        获取服务句柄
        - params:
        -   service: <string>, 服务key
        - returns
        -   self: <RPC>, 返回一个RPC服务句柄.
        """
        self._current_service = service
        return copy.deepcopy(self)

    def call(self, method, **kwargs):
        """
        调用方法
        - params:
        -   method: <string>, 方法key值.
        - **kwargs: 参数字典
        - returns:
        -   json: <json>, formatter: {"state":"调用网络状态", "msg":"调用的方法的返回值"}
        """
        if not self._current_service:
            raise Exception(
                "service is not set, first call self.handle method to set service."
            )
        state, ret = self._getApi(
            self._current_service, self._current_service + "." + method
        )
        if state:
            try:
                m_uri = ret["uri"]
                m_params = ret["params"]
                m_method = ret["method"]
                m_headers = {}
                if "headers" in kwargs:
                    if isinstance(kwargs["headers"], dict):
                        for o in kwargs["headers"]:
                            m_headers[
                                o.lower().replace("http_", "").replace("_", "-")
                            ] = kwargs["headers"][o]
                    else:
                        return {
                            "state": -1,
                            "msg": "http request headers must is dict type.",
                        }
                m_headers["api-token"] = ret["secret"] if ret["secret"] else ""
                params_data = ""
                m_count = 0
                for param in m_params:
                    if param["key"].lower() != "pk":
                        if param["key"].startswith("http_header_") or param[
                            "key"
                        ].startswith("HTTP_HEADER_"):
                            if param["key"] not in m_headers:
                                if param["key"] not in kwargs:
                                    return {
                                        "state": -1,
                                        "msg": "not found parameter '%s'"
                                        % (param["key"]),
                                    }
                                m_headers[
                                    param["key"]
                                    .replace("_", "-")
                                    .replace("http-header-", "")
                                    .replace("HTTP-HEADER-", "")
                                ] = kwargs[param["key"]]
                        else:
                            if param["key"] in kwargs:
                                params_data += (
                                    param["key"]
                                    + "="
                                    + (
                                        parse.quote(kwargs[param["key"]])
                                        if isinstance(kwargs[param["key"]], str)
                                        else parse.quote(str(kwargs[param["key"]]))
                                    )
                                )
                            else:
                                if param["defaultValue"]:
                                    params_data += (
                                        param["key"]
                                        + "="
                                        + (
                                            parse.quote(param["defaultValue"])
                                            if isinstance(param["defaultValue"], str)
                                            else parse.quote(str(param["defaultValue"]))
                                        )
                                    )
                            m_count += 1
                            if m_count < len(m_params):
                                if len(params_data) > 0:
                                    params_data += "&"
                    else:
                        m_uri = m_uri.replace(
                            "{pk}",
                            parse.quote(kwargs[param["key"]])
                            if isinstance(kwargs[param["key"]], str)
                            else parse.quote(str(kwargs[param["key"]])),
                        )
                if params_data:
                    if m_method == u"GET" or m_method == u"DELETE":
                        if m_uri.find("?") >= 0:
                            m_uri += "&" + params_data
                        else:
                            m_uri += "?" + params_data
            except Exception as e:
                return {"state": -1, "msg": e}
            try:
                if m_method == u"GET":
                    logging.info("access api:(%s), method(GET)." % m_uri)
                    state, ret = GET(uri=m_uri, http_headers=m_headers, time_out=15)
                    if state == 200:
                        try:
                            ret = json.loads(str(ret, encoding="utf-8"))
                            return {"state": ret["state"], "msg": ret["msg"]}
                        except Exception as e:
                            return {"state": -1, "msg": e}
                    else:
                        try:
                            if ret:
                                ret = json.loads(str(ret, encoding="utf-8"))
                                return {"state": ret["state"], "msg": ret["msg"]}
                            else:
                                return {"state": state, "msg": "%s" % m_uri}
                        except:
                            return {
                                "state": state,
                                "msg": 'remote call "%s" error.' % m_uri,
                            }
                elif m_method == u"POST":
                    logging.info(
                        "access api:(%s), method(POST),postdata:%s."
                        % (m_uri, kwargs["data"])
                    )
                    state, ret = POST(
                        m_uri,
                        kwargs["data"],
                        content_type=ContentType.JSON,
                        http_headers=m_headers,
                        time_out=15,
                    )
                    if state == 200:
                        try:
                            ret = json.loads(str(ret, encoding="utf-8"))
                            return {"state": ret["state"], "msg": ret["msg"]}
                        except Exception as e:
                            logging.error(e)
                            raise e
                    else:
                        try:
                            if ret:
                                ret = json.loads(str(ret, encoding="utf-8"))
                                return {"state": ret["state"], "msg": ret["msg"]}
                            else:
                                return {"state": state, "msg": "%s" % m_uri}
                        except:
                            return {
                                "state": state,
                                "msg": 'remote call "%s" error.' % m_uri,
                            }
                elif m_method == u"PUT":
                    logging.info(
                        "access api:(%s), method(PUT),postdata:%s."
                        % (m_uri, params_data)
                    )

                    # 还没有写PUT方法
                    raise Exception("urllib PUT方法还没写.")
                elif m_method == u"DELETE":
                    # 还没有写DELETE方法
                    logging.info("access api:(%s), method(DELETE)" % m_uri)
                    raise Exception("urllib delete 方法还没写.")
                else:
                    raise Exception("restful method is error.")
            except Exception as e:
                return {"state": -1, "msg": e}
        else:
            return {"state": -1, "msg": ret}
