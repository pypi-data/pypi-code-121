import json

import requests

from .alarms_helper import AlarmsHelper
from .config_helper import ConfigHelper
from .enterprise_helper import EnterpriseHelper
from .factor_helper import FactorHelper
from .group_helper import GroupHelper
from .group_member_helper import GroupMemberHelper
from .level_helper import LevelHelper
from .logger import Logger
from .response_helper import ResponseHelper
from .response_option_helper import ResponseOptionHelper
from .rules_helper import RulesHelper
from .statistics_helper import StatisticsHelper
from .theme_helper import ThemeHelper
from .user_helper import UserHelper


class SoozAccess(object):
    def __init__(self, name: str, token: str, force_create: bool = True):
        if ConfigHelper.host == "":
            raise ValueError(
                "Please provide a host before instanciating with 'ConfigHelper.host=\"http://<host>\"'"
            )
        if ConfigHelper.verbose == None:
            raise ValueError(
                "Please provide a boolean value to 'verbose' attribute before instanciating with ''ConfigHelper.verbose = <bool>'"
            )

        self.force_create = force_create
        self.session = requests.session()

        self.alarms = AlarmsHelper(self.session)
        self.enterprise = EnterpriseHelper(self.session)
        self.factors = FactorHelper(self.session)
        self.group_members = GroupMemberHelper(self.session)
        self.groups = GroupHelper(self.session)
        self.levels = LevelHelper(self.session)
        self.response_options = ResponseOptionHelper(self.session)
        self.responses = ResponseHelper(self.session)
        self.rules = RulesHelper(self.session)
        self.statistics = StatisticsHelper(self.session)
        self.themes = ThemeHelper(self.session)
        self.users = UserHelper(self.session, name, token)

        Logger.display = ConfigHelper.verbose

    def __enter__(self):
        _, r = self.users.login()
        if r.status_code == 200:
            return self

        if not self.force_create:
            return None

        _, r = self.users.post_user()

        if r.status_code == 200:
            self.users.login()
            return self

        return None

    def __exit__(self, *args, **kwargs):
        self.users.logout()

    @property
    def user_id(self):
        _, r = self.users.login()
        if r.status_code == 200:
            id = json.loads(r.content.decode("utf-8"))["id"]
            r = self.users.logout()
            return id

        _, r = self.users.post_user()
        if r.status_code == 200:
            id = json.loads(r.content.decode("utf-8"))["id"]
            return id

        return None

    @classmethod
    def prepare_users(cls, group_name: str, users: list[str]):
        id_list = [SoozAccess(name, name).user_id for name in users]

        # create group invitations from admin account
        with SoozAccess("admin_dev", "admin_dev") as admin:
            admin.groups.remove_groups()

            content, _ = admin.groups.post_group(group_name, "")
            group_id = content["groupId"]
            admin.group_members.post_group_invite(group_id, id_list)

        # accepts invitations from admin
        for name in users:
            with SoozAccess(name, name) as user:
                user.group_members.put_group_invitation(group_id)
