from common.plat.service_platform import ServicePlatForm
from common.config.config import TEST_TARGET_REPORT_PATH, PROJECT_NAME
from common.data.data_process import DataProcess
from common.plugin.data_plugin import DataPlugin
from common.plugin.file_plugin import FilePlugin
from loguru import logger
from common.data.handle_common import get_system_key
from common.plat.jira_platform import JiraPlatForm
from common.plugin.data_bus import DataBus
from common.common.constant import Constant
from common.plat.ATF_platform import ATFPlatForm


class ATFPlugin(object):

    @classmethod
    def db_ops(self,_key, _sql, env: str=Constant.ENV):
        DataBus.save_init_data()
        return ATFPlatForm.db_ops(_key, _sql, env)

    @classmethod
    def sendResult(self, report_html_path: str = TEST_TARGET_REPORT_PATH):
        if get_system_key(Constant.RUN_TYPE) is not None:
            prjectname=get_system_key('name')
            buildurl=get_system_key('BUILD_URL')
            env=get_system_key(Constant.ENV)
            build_report = buildurl+"allure/"
            _summary=FilePlugin.load_json(f'{report_html_path}/widgets/summary.json')
            _total = DataPlugin.get_data_jpath(_summary,"$.statistic.total")
            _passed= DataPlugin.get_data_jpath(_summary,"$.statistic.passed")
            _failed = DataPlugin.get_data_jpath(_summary, "$.statistic.failed")
            _start = DataProcess.getDate(int(str(DataPlugin.get_data_jpath(_summary, "$.time.start")).strip())/1000)
            _stop = DataProcess.getDate(int(str(DataPlugin.get_data_jpath(_summary, "$.time.stop")).strip())/1000)
            _duration = int(str(DataPlugin.get_data_jpath(_summary, "$.time.duration")).strip())/1000
            _TestType = '自动化回归测试'
            _projectName = PROJECT_NAME
            _result = 'success'
            act_passrate = round((int(str(_passed)) / int(str(_total)))*100,2)
            if get_system_key(Constant.PASS_RATE) is not None and get_system_key(Constant.PASS_RATE).strip() !='':
                passrate = int(str(get_system_key(Constant.PASS_RATE)).replace('%','').strip())
                if act_passrate > passrate:
                    _result = 'success'
                else:
                    _result = 'fail'
            if buildurl.lower().find('smo') != -1:
                _TestType = '自动化冒烟测试'
            if get_system_key(Constant.TEST_TYPE) is not None and get_system_key(Constant.TEST_TYPE).strip() !='':
                _TestType = get_system_key(Constant.TEST_TYPE)
            if get_system_key(Constant.PROJECT_NAME) is not None and get_system_key(Constant.PROJECT_NAME).strip() !='':
                _projectName = get_system_key(Constant.PROJECT_NAME)
            if _total > 0 and _passed > 0:
                if get_system_key(Constant.SEND_URSER_LIST) is not None and get_system_key(Constant.SEND_URSER_LIST).strip() !='':
                    _list = get_system_key(Constant.SEND_URSER_LIST).split(',')
                    if get_system_key(Constant.ISSUE_KEY) is not None and get_system_key(Constant.ISSUE_KEY).strip() !='':
                        _jira_key_url = get_system_key(Constant.ISSUE_KEY)
                        _jira_info = f'JIRA任务：{Constant.JIRA_URL}/browse/{_jira_key_url}'
                    if _result.strip() == 'success':
                        act_passrate_str = f'{act_passrate}' + '%【通过】'
                    else:
                        act_passrate_str = f'{act_passrate}' + '%【失败】'
                    _desc = f'项目名称：{_projectName}\n' \
                            f'执行环境：{env}\n' \
                            f'测试类型：{_TestType}\n' \
                            f'总用例数：{_total}\n' \
                            f'失败用例：{_failed}\n' \
                            f'通过用例：{_passed}\n' \
                            f'测试结果：{act_passrate_str}\n' \
                            f'运行时间：{_duration}S\n' \
                            f'开始时间：{_start}\n' \
                            f'结束时间：{_stop}\n' \
                            f'构建详情：{buildurl} \n ' \
                            f'测试报告：{build_report} \n' \
                            f'{_jira_info}'
                    logger.info(f"推送消息：\n {_desc}")
                    ServicePlatForm.sendMsg(_desc, _list)
                if get_system_key(Constant.ISSUE_KEY) is not None and get_system_key(Constant.ISSUE_KEY).strip() !='':
                    jirakey = get_system_key(Constant.ISSUE_KEY)
                    dict = {"issuekey": f"{jirakey}", "project": f"{prjectname}", "result": f"{_result}"}
                    ATFPlatForm.runDeploy("AutoTest-Result", dict)
                    if _result.strip() == 'success':
                        act_passrate_str = f'{act_passrate}' + '%{color:#00875a}【通过】{color}'
                        JiraPlatForm.setJiraFlowStatus(jirakey, "2551")
                    else:
                        act_passrate_str = f'{act_passrate}' + '%{color:#FF0000}【失败】{color}'
                    _desc = f'项目名称：{_projectName}\\r\\n' \
                            f'运行环境：{env}\\r\\n' \
                            f'测试类型：{_TestType}\\r\\n' \
                            f'总用例数：{_total}\\r\\n' \
                            f'失败用例：{_failed} \\r\\n' \
                            f'通过用例：{_passed}\\r\\n' \
                            f'测试结果：{act_passrate_str}\\r\\n' \
                            f'运行时间：{_duration}S\\r\\n' \
                            f'开始时间：{_start}\\r\\n' \
                            f'结束时间：{_stop}\\r\\n' \
                            f'构建详情： {buildurl}\\r\\n' \
                            f'测试报告：{build_report}'
                    logger.info(f"备注信息：\n {_desc}")
                    JiraPlatForm.setJiraComment(jirakey, _desc)




if __name__ == '__main__':
    _passed='49'
    _total='80'
    act_passrate=round((int(str(_passed)) / int(str(_total)))*100,2)

    print(f'{act_passrate}%')

