import json

from common.common.api_driver import APIDriver
from common.data.handle_common import get_system_key
from common.common.constant import Constant
from requests.auth import HTTPBasicAuth


class JenkinsPlatForm(object):
    @classmethod
    def sendResultByJenkins(self, _issuekey,_projectName,_result):
        """
        推送测试结果到Jenkins的WebHook触发Jira
        :param _issuekey:
        :param _projectName:
        :param _result:
        :return:
        """
        _data = json.dumps(
            '{"parameter": [{"name":"issuekey", "value":"_issuekey"}, {"name":"project", "value":"_projectName"}, {"name":"result", "value":"_result"}]}'
            .replace('_issuekey', _issuekey).replace('_projectName', _projectName).replace("_result", _result))
        _jenkin_deploy=get_system_key(Constant.JENKINS_DEPLOY)
        return APIDriver.http_request(url=f"{_jenkin_deploy}/view/All-deploy/job/AutoTest-Result/buildWithParameters",
                                      method='post',
                                      parametric_key='data',
                                      data=_data,
                                      _auth=HTTPBasicAuth(get_system_key(Constant.JENKINS_DEPLOY_USER),
                                                          get_system_key(Constant.JENKINS_DEPLOY_TOKEN)),
                                      )



