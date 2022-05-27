"""
  @Project     : sentry-dingtalk
  @Time        : 2022/05/26 15:35:12
  @File        : plugin.py
  @Author      : source
  @Software    : VSCode
  @Desc        :
"""


import requests
import six
import ast
from sentry import tagstore
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.utils.http import absolute_uri
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin
from django.conf import settings
class DingTalkPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "DingTalk"
    slug = "dingtalk"
    description = "Post notifications to Dingtalk."
    conf_key = "dingtalk"
    required_field = "webhook"
    author = "source"
    author_url = "https://xxx.xxx.cc/FE/sentry-k8s/-/tree/main/sentry-dingtalk"
    version = "4.1.3"
    resource_links = [
        ("Report Issue", "https://xxx.xxx.cc/FE/sentry-k8s/-/tree/main/sentry-dingtalk/issues"),
        ("View Source", "https://xxx.xxx.cc/FE/sentry-k8s/-/tree/main/sentry-dingtalk"),
    ]

    feature_descriptions = [
        FeatureDescription(
            """
                Configure rule based Dingtalk notifications to automatically be posted into a
                specific channel.
                """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

    def is_configured(self, project):
        return bool(self.get_option("webhook", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "webhook",
                "type": "url",
                "placeholder": "https://oapi.dingtalk.com/robot/send?access_token=**********",
                "required": True,
                "help": "钉钉 webhook 支持@成员",
                "default": self.set_default(project, "webhook", "DINGTALK_WEBHOOK"),
            },
            {
                "name": "project_user",
                "label": "project_user",
                "type": "string",
                "placeholder": "钉钉id,逗号分隔多个",
                "required": True,
                "help": "项目对应负责人",
                "default": self.set_default(
                    project, "project_user", ""
                ),
            }
        ]

    def set_default(self, project, option, env_var):
        if self.get_option(option, project) != None:
            return self.get_option(option, project)
        if hasattr(settings, env_var):
            return six.text_type(getattr(settings, env_var))
        return None

    def notify(self, notification, raise_exception=False):
        event = notification.event
        user = event.get_minimal_user()
        userName = user.username
        release = event.release
        group = event.group
        project = group.project
        self._post(group, userName, release, project)

    def _post(self, group, userName, release, project):
        webhook = self.get_option("webhook", project)
        # 项目负责人
        project_user = self.get_option("project_user", project)
        user_list = project_user.split(",")
        ats_ding_str = ""
        for at in user_list:
            ats_ding_str = f"{ats_ding_str} [@{at}](dingtalk://dingtalkclient/action/sendmsg?dingtalk_id={at})"
            

        issue_link = group.get_absolute_url(params={"referrer": "dingtalk"})

        payload = f"### 「[打叉] 前端监控告警」\n\n"
        payload = f"{payload} #### 项目名：{project.name}\n\n"
        payload = f"{payload} #### 跟进人：{ats_ding_str}\n\n"
        payload = f"{payload} #### 版本：{release} \n\n"
        payload = f"{payload} #### 最新触发用户：{userName} \n\n"
        payload = f"{payload} #### [异常信息]({issue_link}): \n\n"
        payload = f"{payload} > {group.message}…\n\n"
        payload = f"{payload} ###### [客服]请项目负责人及时查看分配处理\n\n"

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "charset": "utf8"
        }

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": f"{project.name}发生告警,问题地址：{issue_link}",
                "text": payload,
            },
            "at": {
                "atDingtalkIds": user_list,
                "isAtAll": "false"
            }
        }
        requests.post(webhook, data=json.dumps(data), headers=headers)
