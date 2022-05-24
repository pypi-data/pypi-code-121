import abc
import json
import sys
import traceback

from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile
from re_common.baselibrary.utils.basetime import BaseTime
from re_common.facade.loggerfacade import get_streamlogger

"""
json 格式如下
{
“step1”：{

“isFinish”：False
}
}
"""


# 执行框架图
class GlobalControl(object):
    def __init__(self, file):
        """

        :param file: 传入__file__
        :param loggerdir:
        """
        self.insert(file)
        self.jsonfile = BaseFile.get_new_path(self.curPath, "run.json")
        self.logger = get_streamlogger()
        # 　False 表示更新没有完成,接着更新　ture 表示新一轮更新已经结束
        self.is_restart = False
        self.nowstep = ""
        self.key = ""
        self.readjson()
        self.basetime = BaseTime()
        self.step_dicts = {}

    @abc.abstractmethod
    def imports(self, dicts=None):
        # raise NotImplementedError python2的方法
        pass

    @abc.abstractmethod
    def set_step_dict(self, dicts):
        pass

    def insert(self, file):
        """
        :param file:  __file__
        :return:
        """
        self.curPath = BaseDir.get_file_dir_absolute(file)
        sys.path.insert(0, self.curPath)  # 插入

    def writejson(self):
        jsonstrings = json.dumps(self.jsondicts, ensure_ascii=False)
        BaseFile.single_write_file(BaseFile.get_new_path(self.curPath, "run.json"),jsonstrings)

    def readjson(self):
        if BaseFile.is_file_exists(self.jsonfile):
            self.logger.info("读取json 文件{}".format(str(self.jsonfile)))
            jsonstrings = BaseFile.single_read_file(self.jsonfile)
            self.logger.info("json　文件内容为：{}".format(jsonstrings))
            if jsonstrings:
                self.jsondicts = json.loads(jsonstrings)
            else:
                self.jsondicts = {}
        else:
            self.logger.info("json　文件不存在,创建空的dicts")
            self.jsondicts = {}

    def check(self):
        if "end" in self.jsondicts.keys() and self.jsondicts["end"]["status"] is True:
            self.logger.info("表示上次程序运行结束，本次是新的更新而不是上次发生意外而进行的继续更新")
            self.is_restart = True
        else:
            self.logger.info("表示更新没有完成")
            self.is_restart = False

    def init(self):
        if not self.jsondicts:
            self.logger.info("新一轮更新开始,对json 进行初始化")
            # 清空字典重新开始
            self.jsondicts = {}
            self.jsondicts["start"] = {}
            self.jsondicts["start"]["time"] = self.basetime.get_beijin_date_strins(format="%Y-%m-%d %H:%M:%S")
            self.jsondicts["start"]["isFinish"] = True

    def start_hook(self, key):
        pass

    @abc.abstractmethod
    def step_fun(self):
        """
        调用方法的字符串
        :return:
        """
        pass

    def start(self):
        """
        该步骤获取应该运行哪个代码
        :return:
        """
        thiskey = ""
        for key in self.jsondicts.keys():
            thiskey = key
            if not self.jsondicts[key]["isFinish"]:
                self.key = key
                self.nowstep = self.step_fun()

                return True
            # 如果要对某一个步骤进行特殊处理,可以在该函数返回True
            if self.start_hook(key):
                return True
        if thiskey == "start":
            self.key = "1"
            self.nowstep = self.step_fun()
            return True

        self.key = str(int(thiskey) + 1)
        self.nowstep = self.step_fun()
        return True

    def run(self, strings):
        """
        该步骤运行代码
        :return:
        """
        try:
            if strings == "end":
                return True
            result = eval(strings)
        except:
            self.logger.info(traceback.format_exc())
            return False
        return result

    def writetrue(self, errmessage="", dicts=None):
        self.jsondicts[self.key] = {}
        self.jsondicts[self.key]["errmessage"] = errmessage
        self.jsondicts[self.key]["isFinish"] = True
        self.jsondicts[self.key]["time"] = self.basetime.get_beijin_date_strins(format="%Y-%m-%d %H:%M:%S")
        if dicts is not None:
            self.jsondicts[self.key]["msg"] = dicts
        self.writejson()

    def writefalse(self, e, dicts=None):
        self.jsondicts[self.key] = {}
        self.jsondicts[self.key]["errmessage"] = str(e)
        self.jsondicts[self.key]["isFinish"] = False
        self.jsondicts[self.key]["time"] = self.basetime.get_beijin_date_strins(format="%Y-%m-%d %H:%M:%S")
        if dicts is not None:
            self.jsondicts[self.key]["msg"] = dicts
        self.writejson()

    @abc.abstractmethod
    def one_check(self):
        """
        该步骤检查代码是否运行完成
        :return:
        """
        pass

    def end(self):
        self.jsondicts["end"] = {}
        self.jsondicts["end"]["status"] = True
        self.jsondicts["end"]["time"] = self.basetime.get_beijin_date_strins(format="%Y-%m-%d %H:%M:%S")
        self.writejson()

    def work(self):
        """
        该函数控制整个流程
        :return:
        """
        self.logger.info("start work.....")
        self.check()
        if self.is_restart:
            return True
        self.init()
        while True:
            result1 = self.start()
            self.logger.info("开始第" + self.key + "步")
            result2 = self.run(self.nowstep)
            result3 = self.one_check()
            if result1 and result2 and result3:
                break
        self.end()
