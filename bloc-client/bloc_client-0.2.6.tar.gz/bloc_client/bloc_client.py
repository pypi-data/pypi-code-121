import json
import os.path
import asyncio
import logging
from copy import deepcopy
from functools import partial
from datetime import datetime
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from multiprocessing import Process, Manager
from concurrent.futures import ProcessPoolExecutor


from bloc_client.internal.gen_uuid import new_uuid
from bloc_client.internal.rabbitmq import RabbitMQ
from bloc_client.function_run_opt import FunctionRunOpt
from bloc_client.function import Function, FunctionGroup
from bloc_client.function_interface import FunctionInterface
from bloc_client.function_run_queue import FunctionRunMsgQueue
from bloc_client.function_run_log import Logger, FunctionRunMsg
from bloc_client.function_to_run_mq_msg import FunctionToRunMqMsg
from bloc_client.internal.http_util import post_to_server, sync_post_to_server
from bloc_client.object_storage import get_data_by_object_storage_key, persist_opt_to_server
from bloc_client.function_run_progress_report import HighReadableFunctionRunProgress, report_function_run_high_readable_progress
from bloc_client.function_run_record import get_functionRunRecord_by_id, report_function_run_finished, report_function_run_start, report_function_run_heartbeat

ServerBasicPathPrefix = "/api/v1/client/"
RegisterFuncPath = "register_functions"


@dataclass
class BlocServerConfig:
    ip: str = ""
    port: int = 0

    @property
    def is_nil(self) -> bool:
        return self.ip == "" or self.port == 0

    @property
    def socket_address(self) -> str:
        return f'{self.ip}:{self.port}'

@dataclass
class RabbitMQServerConfig:
    user: str = ""
    password: str = ""
    host: str = ""
    port: int = 0
    v_host: str = ""

    @property
    def is_nil(self) -> bool:
        return (
            self.user == "" or self.password == "" or 
            self.port == 0 or self.host == ""
        )

@dataclass
class ConfigBuilder:
    server_conf: Optional[BlocServerConfig]=None
    rabbitMQ_conf: Optional[RabbitMQServerConfig]=None
    rabbit: Optional[RabbitMQ]=None

    def set_server(self, ip: str, port: int) -> 'ConfigBuilder':
        self.server_conf = BlocServerConfig(ip=ip, port=port)
        return self
    
    def set_rabbitMQ(
            self,
            user: str, password: str,
            host: str, port: int, v_host: str = ""
    ) -> 'ConfigBuilder':
        self.rabbitMQ_conf = RabbitMQServerConfig(
            user=user, password=password,
            host=host, port=port, v_host=v_host)
        return self
    
    def build_up(self):
        if self.server_conf.is_nil:
            raise Exception("must config bloc-server address")

        if self.rabbitMQ_conf.is_nil:
            raise Exception("must config rabbit config")
        self.rabbit = RabbitMQ(
            self.rabbitMQ_conf.user, self.rabbitMQ_conf.password,
            self.rabbitMQ_conf.host, self.rabbitMQ_conf.port,
            self.rabbitMQ_conf.v_host)


@dataclass
class BlocClient:
    name: str
    function_groups: List[FunctionGroup] = field(default_factory=list)
    configBuilder: ConfigBuilder = field(default=ConfigBuilder())

    @staticmethod
    def new_client(client_name: str) -> "BlocClient":
        return BlocClient(name=client_name)

    def register_function_group(self, new_group_name: str) -> FunctionGroup:
        for i in self.function_groups:
            if i.name == new_group_name:
                raise Exception(f"already exist group_name {i.name}, not allow register anymore")
        
        func_group = FunctionGroup(name=new_group_name)
        self.function_groups.append(func_group)
        return func_group

    def gen_req_server_path(self, *sub_paths: str) -> str:
        return self.configBuilder.server_conf.socket_address + os.path.join(
            ServerBasicPathPrefix,
            *sub_paths)
    
    def get_config_builder(self) -> ConfigBuilder:
        self.configBuilder = ConfigBuilder()
        return self.configBuilder
    
    def test_run_function(
        self, 
        user_func: FunctionInterface,
        params: List[List[Any]]
    ):
        ipts = user_func.ipt_config()
        for ipt_index, ipt in enumerate(ipts):
            must = ipts[ipt_index].must
            if must:
                if len(params) - 1 < ipt_index:
                    raise Exception(
                        f"index {ipt_index} is a cannot be nil ipt, but params has no this data")
                if len(params[ipt_index]) < len(ipts[ipt_index].components):
                    raise Exception(
                        f"index {ipt_index} need {len(ipts[ipt_index].components)} component value, "
                        f"but param only provide {len(params[ipt_index])} value"
                    )

            if ipt_index >= len(params): break
            for component_index, _ in enumerate(ipt.components):
                if component_index >= len(params[ipt_index]):
                    ipts[ipt_index].components[component_index].value = None
                else:
                    ipts[ipt_index].components[component_index].value = params[ipt_index][component_index]
        
        q = FunctionRunMsgQueue.New()
        runner_return_dict = Manager().dict()

        runner = Process(
            target=user_func.run, 
            args=(ipts, q))

        reader = Process(
            target=self._mock_read, 
            args=(q, runner_return_dict))

        runner.start()
        reader.start()
        runner.join()
        reader.join()
        reader.terminate()

        return runner_return_dict['return_value']

    @staticmethod
    async def keep_register_to_server(
        executor, loop,
        url: str, req: Dict[str, Any]
    ):
        while True:
            resp, err = await loop.run_in_executor(
                executor, sync_post_to_server,
                url, req
            )
            if err:
                # TODO
                pass
            await asyncio.sleep(10)
    
    @property
    def register_to_server_dict(self):
        groupName_map_functions = {}
        req = {
            "who": self.name,
            "groupName_map_functions": groupName_map_functions}
        
        for i in self.function_groups:
            group_name = i.name
            groupName_map_functions[group_name] = []
            for j in i.functions:
                groupName_map_functions[group_name].append(
                    Function(
                        name=j.name, 
                        group_name=j.name,
                        description=j.description, 
                        ipts=j.ipts,
                        opts=j.opts,
                        progress_milestones=j.progress_milestones).json_dict())
        return req

    @property
    def register_to_server_url(self) -> str:
        return self.gen_req_server_path(RegisterFuncPath)

    # this func have two responsibilities:
    # 1. register local functions to server
    # 2. get server's resp of each function's id. it's needed in consumer to find func by id
    async def register_functions_to_server(self):
        resp, err = await post_to_server(
            self.register_to_server_url,
            self.register_to_server_dict)
        if err:
            raise Exception(f"register to server failed: {err}")
        groupName_map_functions = resp['groupName_map_functions']

        groupname_map_funcname_map_func_resp = {}
        for group_name, functions in groupName_map_functions.items():
            groupname_map_funcname_map_func_resp[group_name] = {}
            for func_dict in functions:
                if func_dict['name'] not in groupname_map_funcname_map_func_resp[group_name]:
                    groupname_map_funcname_map_func_resp[group_name][func_dict['name']] = {}
                groupname_map_funcname_map_func_resp[group_name][func_dict['name']] = func_dict

        # server response each func's id, need complete to local functions
        for i in self.function_groups:
            group_name = i.name
            for j in i.functions:
                server_resp_func = groupname_map_funcname_map_func_resp.get(group_name, {}).get(j.name)
                if not server_resp_func:
                    raise Exception(f'server resp none of function: {group_name}-{j.name}')
                j.id = server_resp_func['id']

    @classmethod
    def create_function_run_logger(cls, server_url:str, function_run_record_id: str) -> Logger:
        return Logger.New(server_url, function_run_record_id)
    
    @classmethod
    def _mock_read(
        cls,
        q: FunctionRunMsgQueue,
        runner_return_dict,
    ):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s %(levelname)s %(message)s")

        while True:
            msg = q.get(3)
            if isinstance(msg, FunctionRunMsg):
                logging.info(f'received log msg: {msg}')
            elif isinstance(msg, FunctionRunOpt):
                logging.info(f'run finished. opt is: {msg}')
                runner_return_dict['return_value'] = msg
                return
            elif isinstance(msg, HighReadableFunctionRunProgress):
                logging.info(f'progress msg: {msg}')

    @classmethod
    def _read(
        cls,
        trace_id: str,
        span_id: str,
        server_url: str,
        function_run_record_id: str,
        logger: Logger,
        q: FunctionRunMsgQueue,
    ):
        last_report_heartbeat_time = datetime.now()
        while True:
            msg = q.get(3)
            if not msg or (
                (datetime.now() - last_report_heartbeat_time).seconds >= 5 and 
                not isinstance(msg, FunctionRunOpt)
            ):
                last_report_heartbeat_time = datetime.now()
                err = report_function_run_heartbeat(
                    trace_id, span_id,
                    server_url, function_run_record_id)
                if err:
                    logger.error(f"report client heartbeat failed: {err}")

            if not msg: continue

            if isinstance(msg, FunctionRunMsg):
                logger.add_msg(msg)
            elif isinstance(msg, FunctionRunOpt):
                function_run_opt = msg
                if function_run_opt.suc:
                    function_run_opt.optKey_map_briefData = {}
                    function_run_opt.optKey_map_objectStorageKey = {}

                    for opt_key, opt_value in function_run_opt.optKey_map_data.items():
                        resp, err = persist_opt_to_server(
                            trace_id, span_id,
                            server_url,
                            function_run_record_id,
                            opt_key, opt_value)
                        if err:
                            # TODO
                            pass
                        function_run_opt.optKey_map_objectStorageKey[opt_key] = resp['object_storage_key']
                        if isinstance(opt_value, bool):
                            function_run_opt.optKey_map_briefData[opt_key] = str(opt_value)
                        elif isinstance(opt_value, int):
                            function_run_opt.optKey_map_briefData[opt_key] = str(opt_value)
                        elif isinstance(opt_value, float):
                            function_run_opt.optKey_map_briefData[opt_key] = str(opt_value)
                        elif isinstance(opt_value, str):
                            function_run_opt.optKey_map_briefData[opt_key] = opt_value[:50]
                        else:
                            function_run_opt.optKey_map_briefData[opt_key] = resp['brief']

                err = report_function_run_finished(
                    trace_id, span_id,
                    server_url,
                    function_run_record_id,
                    function_run_opt)
                if err:
                    logger.error(f"report function finished failed: {err}")
                else:
                    logger.info(f"report function finished")
                return
            elif isinstance(msg, HighReadableFunctionRunProgress):
                func_run_progress = msg
                err = report_function_run_high_readable_progress(
                    trace_id, span_id,
                    server_url, 
                    function_run_record_id,
                    func_run_progress)

    @classmethod
    def _run_function(
        cls,
        msg_str: str,
        client_name: str,
        server_url: str,
        function_groups: List[FunctionGroup],
    ):
        msg_dict = json.loads(msg_str)
        msg = FunctionToRunMqMsg(**msg_dict)
        if msg.ClientName != client_name:
            raise Exception(f"""
                Big trouble!
                Not mine functions msg routed here!
                {msg_dict}""")
        
        logger = cls.create_function_run_logger(
            server_url, msg.FunctionRunRecordID)
        
        function_run_record, err = get_functionRunRecord_by_id(
            server_url, msg.FunctionRunRecordID)
        if err:
            logger.error(f"get_functionRunRecord_by_id from server error: {err}")
            #TODO
            pass
        
        the_func = None
        for function_group in function_groups:
            if the_func: break
            for f in function_group.functions:
                if f.id == function_run_record.function_id:
                    the_func = deepcopy(f)
                    break

        logger.set_trace_id(function_run_record.trace_id)
        span_id = new_uuid()
        logger.set_span_id(span_id)

        err = report_function_run_start(
            function_run_record.trace_id, span_id,
            server_url, msg.FunctionRunRecordID)
        if err:
            logger.error(f"report function run start to server error: {err}")

        for ipt_index, ipt in enumerate(function_run_record.ipt):
            for component_index, component_brief_and_key in enumerate(ipt):
                value, err = get_data_by_object_storage_key(
                    server_url, component_brief_and_key.object_storage_key,
                    the_func.ipts[ipt_index].components[component_index].value_type,
                    the_func.ipts[ipt_index].components[component_index].allow_multi,
                )
                if err:
                    logger.error(f"""
                        get_data_by_object_storage_key from server error: {err}.
                        ipt_index: {ipt_index}, component_index: {component_index},
                        key:{component_brief_and_key.object_storage_key}""")
                    # TODO
                    pass
                the_func.ipts[ipt_index].components[component_index].value = value

        q = FunctionRunMsgQueue.New()
        # TODO 超时检测

        # before start should send client run this function's heartbeat first
        report_function_run_heartbeat(
            function_run_record.trace_id, span_id,
            server_url, msg.FunctionRunRecordID)

        # start run & keep upload intime msg
        runner = Process(
            target=the_func.exe_func.run, 
            args=(
                the_func.ipts, q,
            )
        )

        reader = Process(
            target=cls._read, 
            args=(
                function_run_record.trace_id,
                span_id,
                server_url,
                msg.FunctionRunRecordID,
                logger,
                q, 
            )
        )
        
        runner.start()
        reader.start()
        runner.join()
        reader.join()
        reader.terminate()
    
    @classmethod
    async def _run_consumer(
        cls,
        executor, 
        loop,
        rabbit: RabbitMQ, 
        name: str,
        client_name: str,
        server_url: str,
        function_groups: List[FunctionGroup],
    ):
        run_func = partial(
            cls._run_function,
            client_name=client_name,
            server_url=server_url,
            function_groups=function_groups,
        )
        rabbit.consume_prepare(name, name)

        channel = rabbit.channel
        while True:
            method_frame, _, body = channel.basic_get(
                name,
                auto_ack=True,
            )
            if method_frame:
                await loop.run_in_executor(
                    executor, run_func, body.decode())
            else:
                await asyncio.sleep(0)

    async def run(self):
        await self.register_functions_to_server()

        loop = asyncio.get_event_loop()
        with ProcessPoolExecutor(max_workers=2) as executor:
            await asyncio.gather(
                self.keep_register_to_server(
                    executor, loop,
                    self.register_to_server_url,
                    self.register_to_server_dict,
                ),
                self._run_consumer(
                    executor,
                    loop,
                    self.configBuilder.rabbit,
                    "function_client_run_consumer." + self.name,
                    self.name, 
                    self.gen_req_server_path(), 
                    self.function_groups
                )
            )
