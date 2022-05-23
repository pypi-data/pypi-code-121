from loguru import logger

from common.common.api_driver import APIDriver

from common.common.constant import Constant

from common.data.handle_common import get_system_key


class ATFPlatForm(object):

    @classmethod
    def db_ops(self, _key, _sql, env: str = Constant.ENV):
        """
        执行SQL操作
        :param _key:
        :param _sql:
        :param env:
        :return:
        """
        if get_system_key(Constant.ENV) is not None:
            env = get_system_key(Constant.ENV)
        sql_type = _sql.strip().split(" ")[0].lower()
        if "select" == sql_type:
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/querySetResult/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sql,
                                               _log=False)
            logger.info(f"执行sql成功:{_sql}")
            return list(_tempdata.json())
        if "insert" == sql_type or "delete":
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/doExecute/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sql)
            logger.info(f"执行sql成功:{_sql}")
            return _tempdata.text
        else:
            logger.error("不支持其他语句类型执行，请检查sql")


    @classmethod
    def runDeploy(self,jobName, _pramater):
        """
        推送测试结果
        :param jobName:
        :param _pramater:
        :return:
        """
        _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL}/jenkins/runDeploy/{jobName}",
                                               method='get', parametric_key='params', data=_pramater)
        return _tempdata
