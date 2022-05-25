def inject_lib_path():
    import os
    import sys
    from pathlib import Path

    dir_path = Path(__file__).parent
    libs_path = dir_path.joinpath(".libs")
    os.environ["PATH"] = ";".join(
        [p for p in [os.environ.get("PATH", ""), libs_path.as_posix()] if p]
    )
    os.environ["LD_LIBRARY_PATH"] = ";".join(
        [
            p
            for p in [
                os.environ.get("LD_LIBRARY_PATH", ""),
                libs_path.as_posix(),
            ]
            if p
        ]
    )
    if sys.version_info.major == 3 and sys.version_info.minor >= 8:
        if sys.platform == "win32":
            os.add_dll_directory(libs_path.as_posix())


inject_lib_path()
del inject_lib_path

import os
import typing
import atexit
import msgpack
import orjson

from pysolace import solclient
from pysolace.solclient import SolLogLevel
from threading import Event, Lock
from loguru import logger
import msgpack
import orjson
from ._version import __version__


class SolClient:
    def __init__(
        self,
        log_level: SolLogLevel = SolLogLevel.SOLCLIENT_LOG_NOTICE,
        debug: bool = False,
    ):
        self.sol = solclient.client(log_level, debug)
        self.msg_callback: typing.Callable[
            [str, dict], None
        ] = lambda topic, msg: print(topic, msg)
        self.p2p_callback: typing.Callable[
            [str, dict], None
        ] = lambda topic, msg: print(topic, msg)
        self.event_callback: typing.Callable[
            [int, int, str, str], None
        ] = lambda resp_code, event, info, event_str: print(
            "Response Code: {} | Event Code: {} | Info: {} | Event: {}".format(
                resp_code, event, info, event_str
            )
        )
        self.session_down_callback: typing.Callable[[], None] = lambda: print(
            "Session Down."
        )
        self.reply_callback: typing.Callable[
            [str, dict, dict], tuple
        ] = lambda topic, header, body: ((1, body), print(topic, header, body))[0]
        self.onreply_callback: typing.Callable[
            [str, str, dict], None
        ] = lambda topic, corrid, reply: print(topic, corrid, reply)
        solclient.set_callback(self.sol, self.msg_callback_wrap)
        solclient.set_p2p_callback(self.sol, self.p2p_callback_wrap)
        solclient.set_event_callback(self.sol, self.event_callback_wrap)
        solclient.set_session_down_callback(self.sol, self.session_down_callback_wrap)
        solclient.set_reply_callback(self.sol, self.reply_callback_wrap)
        solclient.set_onreply_callback(self.sol, self.onreply_callback_wrap)

        # self.set_msg_callback(self.msg_callback_wrap)
        # self.set_p2p_callback(self.p2p_callback_wrap)
        # self.set_event_callback(self.event_callback_wrap)
        self._token: str = ""
        self.req_rep_map: typing.Dict[str, dict] = {}
        self.rep_callback_map: typing.Dict[str, typing.Callable] = {}
        self.rep_event_map: typing.Dict[str, Event] = {}
        self._counter: int = 0
        self._counter_lock: Lock = Lock()
        self._client_name: str = ""
        atexit.register(self.cleanup)

    def _gen_reqid(self):
        with self._counter_lock:
            self._counter += 1
        return "c{}".format(self._counter)

    def msg_callback_wrap(self, topic: str, msg: dict):
        try:
            # with logger.catch():
            self.msg_callback(topic, msg)
        except Exception as e:
            print(e)
        return 0

    def p2p_callback_wrap(self, topic: str, body: dict) -> None:
        if self.p2p_callback:
            with logger.catch():
                self.p2p_callback(topic, body)

    def reply_callback_wrap(
        self, topic: str, header: dict, body: dict
    ) -> typing.Tuple[int, dict]:
        ret = (1, {})
        if self.reply_callback:
            with logger.catch():
                ret = self.reply_callback(topic, header, body)
        return ret

    def event_callback_wrap(
        self, resp_code: int, event: str, info: str, event_str: str
    ):
        with logger.catch():
            self.event_callback(resp_code, event, info, event_str)

    def session_down_callback_wrap(self):
        with logger.catch():
            self.session_down_callback()

    def onreply_callback_wrap(self, topic: str, corrid: str, reply: dict):
        with logger.catch():
            for k, v in reply.items():
                self.req_rep_map[corrid][k] = v
            self.rep_callback_map.get(corrid, self.onreply_callback)(
                topic, corrid, reply
            )
            self.req_rep_map.pop(corrid)
            if corrid in self.rep_event_map:
                recv = self.rep_event_map.pop(corrid)
                recv.set()
            if corrid in self.rep_callback_map:
                self.rep_callback_map.pop(corrid)
        return 0

    def connect(
        self,
        host: str,
        vpn: str,
        user: str,
        password: str,
        clientname: str = "",
        connect_timeout_ms: int = 3000,
        reconnect_retries: int = 10,
        keep_alive_ms: int = 3000,
        reconnect_retry_wait: int = 3000,
        keep_alive_limit: int = 3,
    ):
        """
        connect(host: str, vpn: str, user: str, pass: str, clientname: str='') -> int


        Connect to Solace

        Args:
            host (str): the host of solace to connect
            vpn (str): the vpn of solace
            user (str): the username of solace
            pass (str): the password of solace
            clientname (str) optional: the client name of solace

        Returns:
            CSol Object
        """
        self._client_name = clientname
        return solclient.connect(
            self.sol,
            host,
            vpn,
            user,
            password,
            clientname,
            connect_timeout_ms,
            reconnect_retries,
            keep_alive_ms,
            reconnect_retry_wait,
            keep_alive_limit,
        )

    def set_client_name(self, clientname: str) -> int:
        setted = solclient.set_client_name(self.sol, clientname)
        if setted:
            self._client_name = clientname
        return setted
    
    def get_client_name(self):
        return self._client_name

    def subscribe(self, topic: str):
        """
        subscribe(arg0: str) -> None


        Subscribe topic

        Args:
            topic (str): the topic to subscribe
        """
        solclient.subscribe(self.sol, topic)

    def unsubscribe(self, topic: str):
        """
        unsubscribe(arg0: str) -> None


        UnSubscribe topic

        Args:
            topic (str): the topic to unsubscribe
        """
        solclient.unsubscribe(self.sol, topic)

    def publish(
        self, topic: str, msg: dict, format: str = "msgpack", cos: int = 1
    ) -> int:
        """
        publish(topic: str, msg: dict) -> int


        Publish Message to topic

        Args:
            sol (obj::Csol): the object of solclient return
            topic (str): the topic to subscribe
            msg_dict (dict): message to publish
        """
        return solclient.publish(self.sol, topic, msg, format, cos)

    def publish_raw(
        self, topic: str, content_type: str, buf: bytes, cos: int = 1
    ) -> int:
        return solclient.publish_raw(self.sol, topic, content_type, buf, cos)

    def publish_multi_raw(
        self, msgs: typing.List[typing.Tuple[str, bytes]], content_type: str, cos: int = 1
    ) -> int:
        return solclient.publish_multi_raw(self.sol, msgs, content_type, cos)

    def request(
        self,
        topic: str,
        payload: dict,
        corrid: str = "",
        timeout: int = 5000,
        cos: int = 1,
        format: str = "msgpack",
        cb: typing.Callable[[str, str, dict], int] = None,
    ) -> dict:
        if self._token:
            payload = dict(token=self._token, **payload)
        if not corrid:
            corrid = self._gen_reqid()
        recv = Event()
        self.rep_event_map[corrid] = recv
        if cb:
            self.rep_callback_map[corrid] = cb
        resp = self.req_rep_map[corrid] = solclient.request(
            self.sol, topic, corrid, payload, 0, cos, format
        )
        if timeout and not recv.wait(timeout / 1000):
            raise TimeoutError(
                "Topic: {}, Corr: {}, Client: {}, payload: {}".format(
                    topic, corrid, self._client_name, payload
                )
            )
        return resp

    def reply(self, topic: str, header: dict, body: dict):
        return solclient.reply(self.sol, topic, header, body)

    def get_msg_queue_size(self):
        return solclient.get_msg_queue_size(self.sol)

    def set_session(self, token: str):
        self._token = token

    def set_msg_callback(self, callback_func: callable):
        """
        set_callback(arg0: Callable[[str, dict], int]) -> None

        Set subscribe using callback function

        Args:
            func (py::func): the python callable function the func first arg is topic
                            second arg is message and return int

        Examples:
            Examples with Doctest format
            >>> def sol_callback(topic, msg):
            >>>     print(topic, msg)
        """
        self.msg_callback = callback_func
        # solclient.set_callback(self.sol, self.msg_callback_wrap)

    def set_event_callback(self, callback_func: callable):
        """
        set_event_callback(arg0: Callable[[int, int, str, str], None]) -> None

        Set subscribe using callback function

        Args:
            func (py::func): the python callable function the func with
                            arg0: response code
                            arg1: session event code
                            arg2: info string
                            arg3: session event string

        Examples:
            Examples with Doctest format
            >>> def event_callback(response_code, event_code, info, event):
            >>>     print(response_code, event_code, info, event)
        """
        self.event_callback = callback_func
        # solclient.set_event_callback(self.sol, self.event_callback_wrap)

    def set_session_down_callback(self, callback_func: callable):
        """
        set_event_callback(arg0: Callable[[int, int, str, str], None]) -> None

        Set subscribe using callback function

        Args:
            func (py::func): the python callable function the func with

        Examples:
            Examples with Doctest format
            >>> def event_callback():
            >>>     print("Session Down.")
        """
        self.session_down_callback = callback_func
        # solclient.set_event_callback(self.sol, self.event_callback_wrap)

    def set_p2p_callback(self, func: callable):
        self.p2p_callback = func
        # solclient.set_p2p_callback(self.sol, self.p2p_callback_wrap)

    def set_reply_callback(self, callable_func: callable):
        self.reply_callback = callable_func
        # solclient.set_reply_callback(self.sol, self.reply_callback_wrap)

    def set_onreply_callback(self, callable_func: callable):
        self.onreply_callback = callable_func
        # solclient.set_onreply_callback(self.sol, self.onreply_callback_wrap)

    def disconnect(self):
        if self.sol:
            return solclient.disconnect(self.sol)

    def cleanup(self):
        if self.sol:
            solclient._del(self.sol)
            self.sol = 0

    def __del__(self):
        if self.sol:
            self.cleanup()
