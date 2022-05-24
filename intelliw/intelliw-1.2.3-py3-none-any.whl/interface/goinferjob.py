import os
import subprocess

import intelliw.utils.message as message
from intelliw.config import config
from intelliw.core.report import RestReport
from intelliw.utils.gen_high_performance_cfg import convert_model_config
from intelliw.utils.logger import get_logger

logger = get_logger()
infer_path = "/root/intelliw/infer"
#infer_config_name = "infer_model.yaml"
infer_config_name = "model.yaml"



def get_env(path, response_addr):
    infer_lib = infer_path + "/lib"
    infer_lib_deps = infer_lib + "/deps"
    ld_library_path = infer_lib + ":/usr/local/lib:" + os.path.join(path, "lib")
    ld_library_path += ":{}/tensorflow/v2.0.1/cpu/deps/lib:{}/tensorflow/v2.3.1/cpu/deps/lib".format(infer_lib_deps,
                                                                                                     infer_lib_deps)
    ld_library_path += ":{}/lightgbm/v3.1.1/deps/lib".format(infer_lib_deps)
    ld_library_path += ":{}/paddle/v1.7/cpu/deps/lib:{}/paddle/v2.0.0/gpu/deps/lib".format(infer_lib_deps,
                                                                                           infer_lib_deps)

    env = {"LD_LIBRARY_PATH": ld_library_path, "INFER_ID": config.INFER_ID, "INSTANCE_ID": config.INSTANCE_ID,
           "SERVICE_ID": config.SERVICE_ID, "TOKEN": config.TOKEN, "PERODIC_INTERVAL": config.PERODIC_INTERVAL,
           "TENANT_ID": config.TENANT_ID, "API_EXTRAINFO": config.API_EXTRAINFO, "REPORT_ADDR": response_addr,
           "IS_SPECIALIZATION": config.IS_SPECIALIZATION}
    for i in env:
        if type(env[i]) == str:
            continue
        if type(env[i]) == bool:
            if env[i]:
                env[i] = "true"
            else:
                env[i] = "false"
            continue
        if env[i] is not None:
            env[i] = str(env[i])
        else:
            env[i] = ""
    return env


class InferService:
    def __init__(self, name, port, path, response_addr):
        self.name = name  # 'predict'
        self.port = port  # 8888
        self.path = path
        self.addr = response_addr
        self.reporter = RestReport(response_addr)
        self.response_addr = response_addr

    def check(self):
        self.prepare("infertools", "importmodel")
        args = "{} check --path {}".format(os.path.join(infer_path, "infertools"),
                                           os.path.join(self.path, infer_config_name))
        self.run_cmd("check", args, get_env(self.path, self.response_addr))
        self.reporter.report(message.ok_import_model)
        logger.info("check high performance infer engine successful")

    def run(self):
        self.prepare("infer", "apiservice")
        if self.addr is None:
            args = "{} -c {} ".format(os.path.join(infer_path, "infer"),
                                      os.path.join(self.path, infer_config_name))
        else:
            args = "{} -c {} -addr {}".format(os.path.join(infer_path, "infer"),
                                              os.path.join(self.path, infer_config_name), self.addr)
        self.run_cmd("start", args, get_env(self.path, self.response_addr))

    def prepare(self, cmd, status):
        if not os.path.isfile(os.path.join(infer_path, cmd)):
            self.reporter.report(message.CommonResponse(500, status, "can not find executable file {}".format(cmd)))
            raise Exception("can not find high performance executable file {}".format(cmd))


        # cfg = load_config(os.path.join(self.path, infer_config_name))
        # if config.IS_SPECIALIZATION == 0 and  not cfg.get('Infer'):
        # if config.IS_SPECIALIZATION == 0 and not os.path.isfile(os.path.join(self.path, infer_config_name)):
        if config.IS_SPECIALIZATION == 0:
            convert_model_config(self.path)

        self.run_cmd("prepare", "chmod +x {}".format(os.path.join(infer_path, cmd)))
        self.run_cmd("prepare", "mkdir -p {}".format(os.path.join(infer_path, "logs/sys")))

    def run_cmd(self, typ, args=None, env=None):
        if env is not None:
            ret = subprocess.run(args,
                                 shell=True,
                                 capture_output=False,
                                 check=False,
                                 env=env,
                                 encoding="utf-8")
        else:
            ret = subprocess.run(args,
                                 shell=True,
                                 capture_output=False,
                                 check=False,
                                 encoding="utf-8")

        if ret.returncode != 0:
            self.reporter.report(message.CommonResponse(500, "inferstatus", ret.stderr))
            logger.error("{} high performance infer engine error {}".format(typ, ret.stderr))
            raise Exception("{} high performance infer engine error {}".format(typ, ret.stderr))
