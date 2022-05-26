# -*- coding: utf-8 -*-
from io import BytesIO

from attr import asdict
from swimlane import Swimlane
from swimlane.exceptions import SwimlaneHTTP400Error

# Copyright: (c) 2022, Swimlane <info@swimlane.com>
# MIT License (see LICENSE or https://opensource.org/licenses/MIT)
from .decorators import log_exception
from .models import (
    Asset,
    Dashboard,
    Group,
    Package,
    Plugin,
    PluginLight,
    Report,
    Role,
    Task,
    TaskLight,
    User,
    UserLight,
    Workspace,
)
from .utils.exceptions import AddComponentError


class SwimlaneInstance:

    """Creates a connection to a single Swimlane instance"""

    def __init__(
        self,
        host="https://sw_web:4443",
        username=None,
        password=None,
        access_token=None,
        verify_ssl=False,
        verify_server_version=False,
        default_timeout=300,
        resource_cache_size=0,
        write_to_read_only=False,
    ):
        if username and password:
            self.swimlane = Swimlane(
                host=host,
                username=username,
                password=password,
                verify_ssl=verify_ssl,
                verify_server_version=verify_server_version,
                default_timeout=default_timeout,
                resource_cache_size=resource_cache_size,
                write_to_read_only=write_to_read_only,
            )
        elif access_token:
            self.swimlane = Swimlane(
                host=host,
                access_token=access_token,
                verify_ssl=verify_ssl,
                verify_server_version=verify_server_version,
                default_timeout=default_timeout,
                resource_cache_size=resource_cache_size,
                write_to_read_only=write_to_read_only,
            )
        else:
            raise AttributeError("Please provide either a username and password or a access token!")
        self.__workflow_dict = {}
        self.__dashboard_dict = {}

    @property
    def application_dict(self):
        return_dict = {}
        for item in self.get_applications_light():
            if item and item.get("name") and item["name"] not in return_dict:
                return_dict[item["name"]] = item
        return return_dict

    @property
    def application_id_list(self):
        return_list = []
        app_dict = self.application_dict
        if app_dict:
            for key, val in app_dict.items():
                if val.get("id"):
                    return_list.append(val["id"])
        return return_list

    @property
    def plugin_dict(self):
        return_dict = {}
        plugins = self.get_plugins()
        if plugins:
            for item in plugins:
                if item:
                    plugin = self.get_plugin(item.id)
                    if plugin and hasattr(plugin, "fileId"):
                        return_dict[item.name] = plugin.fileId
        return return_dict

    @property
    def workflow_dict(self):
        if not self.__workflow_dict:
            workflows = self.get_workflows()
            if workflows:
                for workflow in workflows:
                    app_dict = self.application_dict
                    if app_dict:
                        for name, item in app_dict.items():
                            if item and item.get("id") and workflow.get("applicationId") == item["id"]:
                                self.__workflow_dict[name] = workflow
        return self.__workflow_dict

    @property
    def dashboard_dict(self):
        if not self.__dashboard_dict:
            for dashboard in self.get_dashboards():
                if dashboard.name not in self.__dashboard_dict:
                    self.__dashboard_dict[dashboard.name] = dashboard.id
        return self.__dashboard_dict

    def _make_request(self, method, endpoint, json=None):
        resp = self.swimlane.request(method, endpoint, json=json)
        if resp and resp.ok:
            if hasattr(resp, "json") and resp.json():
                return resp.json()
            else:
                return resp

    @log_exception
    def get_credentials(self):
        """Used to retrieve keystore items

        Returns:
            dict : A dictionary of keystore keys and encrypted values
        """
        return self._make_request("GET", "/credentials")

    @log_exception
    def get_credential(self, name: str):
        """Retrieves a keystore item if it exists on the desired instance

        Args:
            name (str): Name of a keystore item

        Returns:
            dict : A dictionary of a keystore item
        """
        try:
            return self._make_request("GET", f"/credentials/{name}")
        except Exception as e:
            return False

    @log_exception
    def add_credential(self, credential: dict):
        """Used to add a keystore key name (but not it's value) to a Swimlane instance

        Args:
            credential (dict): A keystore item to add to a Swimlane instance

        Returns:
            dict : A dictionary of a keystore item
        """
        return self._make_request("POST", "/credentials", json=credential)

    @log_exception
    def get_tasks(self):
        """Retrieves a list of tasks for a Swimlane instance.

        These tasks are modeled after the `TaskLight` data model

        Returns:
            list: A list of TaskLight objects
        """
        return_list = []
        tasks = self._make_request("GET", "/task/list")
        if tasks and tasks.get("tasks"):
            for task in tasks["tasks"]:
                return_list.append(TaskLight(**task))
        return return_list

    @log_exception
    def get_task(self, task_id: str):
        """Gets an task by a provided task ID.

        If the task ID does not exist, then this method returns False.

        If the task ID does exist it will return an `Task` object

        Args:
            task_id (str): A task ID to retrieve the entire `Task` object

        Returns:
            Task: A `Task` data model object
        """
        try:
            return Task(**self._make_request("GET", f"/task/{task_id}"))
        except TypeError as te:
            from .utils.exceptions import ModelError

            raise ModelError(err=te, name="Task")
        except Exception as e:
            return False

    def add_task(self, task: Task):
        """Adds a provided Task object to a Swimlane instance

        Args:
            task (Task): A `Task` data model object

        Returns:
            Task: A `Task` data model object
        """
        try:
            return Task(**self._make_request("POST", "/task", json=asdict(task)))
        except Exception as e:
            AddComponentError(model=task, name=task.name, reason=e.__dict__.get("argument"))
            return False

    @log_exception
    def update_task(self, task_id: str, task: Task):
        """Updates a provided task ID with the data contained in the provided `Task` data model object

        Args:
            task_id (str): A task ID to update on a Swimlane instance
            task (Task): A `Task` data model object

        Returns:
            Task: A `Task` data model object
        """
        return Task(**self._make_request("PUT", f"/task/{task_id}", json=asdict(task)))

    @log_exception
    def get_plugins(self):
        """Retrieves a list of plugins for a Swimlane instance.

        These plugins are modeled after the `PluginLight` data model

        Returns:
            list: A list of PluginLight objects
        """
        return_list = []
        plugins = self._make_request("GET", "/task/packages")
        if plugins and isinstance(plugins, list):
            for item in plugins:
                if item:
                    return_list.append(PluginLight(**item))
        return return_list

    @log_exception
    def get_plugin(self, name: str):
        """Gets an plugin by a provided plugin name

        If the plugin does not exist, then this method returns False.

        If the plugin does exist it will return an `Plugin` object

        Args:
            name (str): A plugin name

        Returns:
            Plugin: A `Plugin` data model object
        """
        try:
            return Plugin(**self._make_request("GET", f"/task/packages/{name}"))
        except Exception as e:
            return False

    @log_exception
    def download_plugin(self, file_id: str):
        """A Swimlane internal fileId for a plugin or Python package to download

        Args:
            file_id (str): An internal Swimlane fileId to download a plugin or python package

        Returns:
            BytesIO: A bytesIO object of the downloaded file
        """
        stream = BytesIO()
        response = self.swimlane.request("GET", f"attachment/download/{file_id}", stream=True)
        for chunk in response.iter_content(1024):
            stream.write(chunk)
        stream.seek(0)
        return stream

    @log_exception
    def upload_plugin(self, filename, stream):
        """Uploads a plugin to a Swimlane instance given a filename and a BytesIO file stream

        Args:
            filename (str): A filename string
            stream (BytesIO): A BytesIO file stream

        Returns:
            json: JSON Response from uploading a plugin
        """
        if not filename.endswith(".swimbundle"):
            filename = filename.split(".")[0] + ".swimbundle"
        return self.swimlane.request("POST", "/task/packages", files={"file": (filename, stream.read())}).json()

    @log_exception
    def upgrade_plugin(self, filename, stream):
        """Uploads a plugin to be upgraded on a Swimlane instance given a filename and a BytesIO file stream

        Args:
            filename (str): A filename string
            stream (BytesIO): A BytesIO file stream

        Returns:
            json: JSON Response from uploading a plugin
        """
        if not filename.endswith(".swimbundle"):
            filename = filename.split(".")[0] + ".swimbundle"
        return self.swimlane.request("POST", "/task/packages/upgrade", files={"file": (filename, stream.read())}).json()

    @log_exception
    def get_pip_packages(self, versions=["Python2_7", "Python3_6", "Python3"]):
        """Retrieves a list of pip packages for a Swimlane instance.

        These packages are modeled after the `Package` data model

        Args:
            versions (list, optional): A list of Python versions. Defaults to ['Python2_7', 'Python3_6', 'Python3'].

        Returns:
            list: A list of `Package` objects
        """
        return_list = []
        for version in versions:
            try:
                resp = self._make_request("GET", f"/pip/packages/{version}")
                if resp:
                    for item in resp:
                        return_list.append(Package(**item))
            except Exception as e:
                continue
        return return_list

    @log_exception
    def install_package(self, package: Package):
        """Installs a Python (pip) package based on the provided Package data model object

        Args:
            package (Package): A `Package` data model object

        Returns:
            dict: A dictionary of a Python pip package
        """
        json = {
            "name": package.name,
            "version": package.version,
            "pythonVersion": package.pythonVersion,
        }
        return self._make_request("POST", "/pip/packages", json=json)

    @log_exception
    def install_package_offline(self, filename, stream, data):
        """Installs a Python package wheel file offline to a Swimlane instance given a filename and a BytesIO file stream

        Args:
            filename (str): A filename string
            stream (BytesIO): A BytesIO file stream
            data (dict): A dictionary of additional request information

        Returns:
            json: JSON Response from installing a Python package wheel file
        """
        return self.swimlane.request(
            "POST",
            "/pip/packages/offline",
            data=data,
            files={"wheel": (filename, stream.read())},
            timeout=120,
        )

    @log_exception
    def get_assets(self):
        """Retrieves a list of assets for a Swimlane instance.

        These assets are modeled after the `Asset` data model

        Returns:
            list: A list of `Asset` objects
        """
        return_list = []
        assets = self._make_request("GET", "/asset")
        if assets and isinstance(assets, list):
            for asset in assets:
                return_list.append(Asset(**asset))
        return return_list

    @log_exception
    def get_asset(self, asset_id: str):
        """Gets an asset by a provided ID

        If the asset does not exist, then this method returns False.

        If the asset does exist it will return an `Asset` object

        Args:
            asset_id (str): An Swimlane asset ID

        Returns:
            Asset: An `Asset` data model object
        """
        try:
            return Asset(**self._make_request("GET", f"/asset/{asset_id}"))
        except Exception as e:
            return False

    @log_exception
    def add_asset(self, asset: Asset):
        """Adds a provided Asset object to a Swimlane instance

        Args:
            asset (Asset): An `Asset` data model object

        Returns:
            Asset: An `Asset` data model object
        """
        return Asset(**self._make_request("POST", "/asset", json=asdict(asset)))

    @log_exception
    def update_asset(self, asset_id: str, asset: Asset):
        """Updates a provided asset ID with the data contained in the provided Asset data model object

        Args:
            asset_id (str): An asset ID to update on a Swimlane instance
            asset (Asset): An `Asset` data model object

        Returns:
            Asset: An `Asset` data model object
        """
        return Asset(**self._make_request("PUT", f"/asset/{asset_id}", json=asdict(asset)))

    @log_exception
    def get_applications(self):
        """Retrieves a list of applications for a Swimlane instance.

        Returns:
            list: A list of json objects
        """
        return self._make_request("GET", "/app")

    @log_exception
    def get_application(self, application_id):
        """Gets an application by a provided ID

        If the application does not exist, then this method returns False.

        If the application does exist it will return an JSON object

        Args:
            application_id (str): A Swimlane application ID

        Returns:
            json: A Swimlane application JSON
        """
        try:
            return self._make_request("GET", f"/app/{application_id}")
        except Exception as e:
            return False

    @log_exception
    def get_applications_light(self):
        """Gets light version of all applications

        Returns:
            list: A list of application light objects
        """
        return self._make_request("GET", "/app/light")

    @log_exception
    def update_application(self, application):
        """Updates the application based on the provided dictionary object

        Args:
            application (dict): A application dictionary object.

        Returns:
            dict: A Swimlane application object
        """
        return self._make_request("PUT", "/app", json=application)

    @log_exception
    def add_application(self, application):
        """Adds an application based on the provided dictionary object

        Args:
            application (dict): A application dictionary object.

        Returns:
            dict: A Swimlane application object
        """
        return self._make_request("POST", "/app", json=application)

    @log_exception
    def get_default_report_by_application_id(self, application_id):
        """Gets the default report for an application based on the provided ID

        Args:
            application_id (str): A application dictionary object.

        Returns:
            dict: A Swimlane application object
        """
        try:
            return Report(**self._make_request("GET", f"/reports/app/{application_id}/default"))
        except Exception as e:
            return False

    @log_exception
    def get_workspaces(self):
        """Retrieves a list of workspaces for a Swimlane instance.

        These workspaces are modeled after the `Workspace` data model

        Returns:
            list: A list of `Workspace` objects
        """
        return_list = []
        workspaces = self._make_request("GET", "/workspaces")
        if workspaces:
            for workspace in workspaces:
                return_list.append(Workspace(**workspace))
        return return_list

    @log_exception
    def get_workspace(self, workspace_id: str):
        """Gets an workspace by a provided ID

        If the workspace does not exist, then this method returns False.

        If the workspace does exist it will return an `Workspace` object

        Args:
            workspace_id (str): A Swimlane workspace ID

        Returns:
            Workspace: A `Workspace` data model object
        """
        try:
            return Workspace(**self._make_request("GET", f"/workspaces/{workspace_id}"))
        except Exception as e:
            return False

    @log_exception
    def add_workspace(self, workspace: Workspace):
        """Adds a provided Workspace object to a Swimlane instance

        Args:
            workspace (Workspace): A `Workspace` data model object

        Returns:
            Workspace: A `Workspace` data model object
        """
        return Workspace(**self._make_request("POST", "/workspaces", json=asdict(workspace)))

    @log_exception
    def update_workspace(self, workspace_id: str, workspace: Workspace):
        """Updates a provided workspace ID with the data contained in the provided Workspace data model object

        Args:
            workspace_id (str): A workspace ID to update on a Swimlane instance
            workspace (Workspace): A `Workspace` data model object

        Returns:
            Workspace: A `Workspace` data model object
        """
        return Workspace(**self._make_request("PUT", f"/workspaces/{workspace_id}", json=asdict(workspace)))

    @log_exception
    def get_dashboards(self):
        """Retrieves a list of dashboards for a Swimlane instance.

        These dashboards are modeled after the `Dashboard` data model

        Returns:
            list: A list of `Dashboard` objects
        """
        return_list = []
        dashboards = self._make_request("GET", "/dashboard")
        if dashboards and isinstance(dashboards, list):
            for dashboard in dashboards:
                return_list.append(Dashboard(**dashboard))
        return return_list

    @log_exception
    def get_dashboard(self, dashboard_id: str):
        """Gets an dashboard by a provided ID

        If the dashboard does not exist, then this method returns False.

        If the dashboard does exist it will return an `Dashboard` object

        Args:
            dashboard_id (str): A Swimlane dashboard ID

        Returns:
            Dashboard: A `Dashboard` data model object
        """
        try:
            return Dashboard(**self._make_request("GET", f"/dashboard/{dashboard_id}"))
        except Exception as e:
            return False

    @log_exception
    def update_dashboard(self, dashboard: Dashboard):
        """Updates a Swimlane instance dashboard based on the provided Dashboard data model object

        Args:
            dashboard (Dashboard): A `Dashboard` data model object

        Returns:
            Dashboard: A `Dashboard` data model object
        """
        return Dashboard(**self._make_request("PUT", f"/dashboard/{dashboard.id}", json=asdict(dashboard)))

    @log_exception
    def add_dashboard(self, dashboard: Dashboard):
        """Adds a provided Dashboard object to a Swimlane instance

        Args:
            dashboard (Dashboard): A `Dashboard` data model object

        Returns:
            Dashboard: A `Dashboard` data model object
        """
        return Dashboard(**self._make_request("POST", "/dashboard", json=asdict(dashboard)))

    @log_exception
    def get_reports(self):
        """Retrieves a list of reports for a Swimlane instance.

        These reports are modeled after the `Report` data model

        Returns:
            list: A list of `Report` objects
        """
        return_list = []
        reports = self._make_request("GET", "/reports")
        if reports:
            for report in reports:
                return_list.append(Report(**report))
        return return_list

    @log_exception
    def get_report(self, report_id: str):
        """Gets an report by a provided ID

        If the report does not exist, then this method returns False.

        If the report does exist it will return an `Report` object

        Args:
            report_id (str): A Swimlane report ID

        Returns:
            Report: A `Report` data model object
        """
        try:
            return Report(**self._make_request("GET", f"/reports/{report_id}"))
        except Exception as e:
            return False

    @log_exception
    def add_report(self, report: Report):
        """Adds a provided `Report` object to a Swimlane instance

        Args:
            report (Report): A `Report` data model object

        Returns:
            Report: A `Report` data model object
        """
        return Report(**self._make_request("POST", "/reports", json=asdict(report)))

    @log_exception
    def update_report(self, report_id: str, report: Report):
        """Updates a provided report ID with the data contained in the provided Report data model object

        Args:
            report_id (str): A report ID to update on a Swimlane instance
            report (Report): A `Report` data model object

        Returns:
            Report: A `Report` data model object
        """
        resp = self._make_request("PUT", f"/reports/{report_id}", json=asdict(report))
        if resp:
            return True

    @log_exception
    def update_default_report(self, report: Report):
        """Updates a Swimlane applications default report with the data contained in the provided `Report` data model object

        Args:
            report (Report): A `Report` data model object

        Returns:
            Report: A `Report` data model object
        """
        return Report(**self._make_request("PUT", f"/reports/{report.id}", json=asdict(report)))

    @log_exception
    def get_users(self):
        """Retrieves a list of users for a Swimlane instance.

        These users are modeled after the `User` data model

        Returns:
            list: A list of `User` objects
        """
        user_list = []
        users = self._make_request("GET", "/user/light")
        if users:
            for user in users:
                user_list.append(UserLight(**user))
        return user_list

    @log_exception
    def get_user(self, user_id: str):
        """Gets an user by a provided ID

        If the user does not exist, then this method returns False.

        If the user does exist it will return an `User` object

        Args:
            user_id (str): A Swimlane user ID

        Returns:
            User: A `User` data model object
        """
        try:
            return User(**self._make_request("GET", f"/user/{user_id}"))
        except Exception as e:
            return False

    @log_exception
    def search_user(self, query_string: str):
        """Searches for a user by a query string

        If the user does not exist, then this method returns False.

        If the user does exist it will return an `User` object

        Args:
            query_string (str): A query string typically a display name

        Returns:
            User: A `User` data model object
        """
        try:
            resp = self._make_request("GET", f"/user/lookup?name={query_string}")
            if resp and isinstance(resp, list):
                return UserLight(**resp[0])
        except Exception as e:
            return False

    @log_exception
    def add_user(self, user: User):
        """Adds a provided User object to a Swimlane instance

        Args:
            user (User): A `User` data model object

        Returns:
            User: A `User` data model object
        """
        return User(**self._make_request("POST", "/user", json=asdict(user)))

    @log_exception
    def update_user(self, user_id: str, user: User):
        """Updates a provided user ID with the data contained in the provided User data model object

        Args:
            user_id (str): A user ID to update on a Swimlane instance
            user (User): A `User` data model object

        Returns:
            User: A `User` data model object
        """
        return User(**self._make_request("PUT", f"/user/{user_id}", json=asdict(user)))

    @log_exception
    def get_groups(self):
        """Retrieves a list of groups for a Swimlane instance.

        These groups are modeled after the `Group` data model

        Returns:
            list: A list of `Group` objects
        """
        return_list = []
        groups = self._make_request("GET", "/groups")
        if groups and groups.get("items"):
            for item in groups["items"]:
                if item:
                    return_list.append(Group(**item))
        elif groups and groups.get("groups"):
            for item in groups["groups"]:
                if item:
                    return_list.append(Group(**item))
        return return_list

    @log_exception
    def get_group_by_name(self, group_name: str):
        """Gets an group by a provided name

        If the group does not exist, then this method returns False.

        If the group does exist it will return an `Group` object

        Args:
            group_name (str): A Swimlane group name

        Returns:
            Group: A `Group` data model object
        """
        try:
            resp = self._make_request("GET", f"/users/lookup?name={group_name}")
            if resp and isinstance(resp, list):
                return Group(**resp[0])
        except Exception as e:
            return False

    @log_exception
    def get_group_by_id(self, group_id: str):
        """Gets an group by a provided id

        If the group does not exist, then this method returns False.

        If the group does exist it will return an `Group` object

        Args:
            group_id (str): A Swimlane group ID

        Returns:
            Group: A `Group` data model object
        """
        try:
            return Group(**self._make_request("GET", f"/groups/{group_id}"))
        except Exception as e:
            return False

    @log_exception
    def add_group(self, group: Group):
        """Adds a provided Group object to a Swimlane instance

        Args:
            group (Group): A `Group` data model object

        Returns:
            Group: A `Group` data model object
        """
        try:
            return Group(**self._make_request("POST", "/groups", json=asdict(group)))
        except SwimlaneHTTP400Error as sh:
            if sh.code == 1051:
                return True
            else:
                raise sh
        except Exception as e:
            raise e

    @log_exception
    def update_group(self, group_id: str, group: Group):
        """Updates a provided group ID with the data contained in the provided Group data model object

        Args:
            group_id (str): A group ID to update on a Swimlane instance
            group (Group): A `Group` data model object

        Returns:
            Group: A `Group` data model object
        """
        return Group(**self._make_request("PUT", f"/groups/{group_id}", json=asdict(group)))

    @log_exception
    def get_roles(self):
        """Retrieves a list of roles for a Swimlane instance.

        These roles are modeled after the `Role` data model

        Returns:
            list: A list of `Role` objects
        """
        return_list = []
        roles = self._make_request("GET", "/roles")
        if roles and isinstance(roles, dict):
            # checking for items here. 10.4.0 does not use the items key
            # but greater versions do (e.g. 10.5>)
            if roles.get("items"):
                roles = roles["items"]
        if roles and isinstance(roles, list):
            for role in roles:
                return_list.append(Role(**role))
        return return_list

    @log_exception
    def get_role(self, role_id: str):
        """Gets an role by a provided ID

        If the role does not exist, then this method returns False.

        If the role does exist it will return an `Role` object

        Args:
            role_id (str): A Swimlane role ID

        Returns:
            Role: A `Role` data model object
        """
        try:
            return Role(**self._make_request("GET", f"/roles/{role_id}"))
        except Exception as e:
            return False

    @log_exception
    def get_role_by_name(self, role_name: str):
        """Gets an role by a provided name

        If the role does not exist, then this method returns False.

        If the role does exist it will return an `Role` object

        Args:
            role_name (str): A Swimlane role name

        Returns:
            Role: A `Role` data model object
        """
        try:
            return Role(**self._make_request("GET", f"/roles/?searchFieldName=name&searchValue={role_name}"))
        except Exception as e:
            return False

    @log_exception
    def add_role(self, role: Role):
        """Adds a provided `Role` object to a Swimlane instance

        Args:
            role (Role): A `Role` data model object

        Returns:
            Role: A `Role` data model object
        """
        return Role(**self._make_request("POST", "/roles", json=asdict(role)))

    @log_exception
    def update_role(self, role_id: str, role: Role):
        """Updates a provided role ID with the data contained in the provided Role data model object

        Args:
            role_id (str): A role ID to update on a Swimlane instance
            role (Role): A `Role` data model object

        Returns:
            Role: A `Role` data model object
        """
        return self._make_request("PUT", f"/roles/{role_id}", json=asdict(role))

    @log_exception
    def get_workflows(self):
        """Retrieves a list of workflows for a Swimlane instance.

        These workflow are modeled after the `Workflow` data model

        Returns:
            list: A list of `Workflow` objects
        """
        return_list = []
        workflows = self._make_request("GET", "/workflow/")
        if workflows:
            for workflow in workflows:
                return_list.append(workflow)
        return return_list

    @log_exception
    def get_workflow(self, application_id: str):
        """Gets an workflow by a provided application ID

        If the workflow does not exist, then this method returns False.

        If the workflow does exist it will return an `Workflow` object

        Args:
            application_id (str): A Swimlane application ID

        Returns:
            Workflow: A `Workflow` data model object
        """
        try:
            return self._make_request("GET", f"/workflow/{application_id}")
        except Exception as e:
            return False

    @log_exception
    def add_workflow(self, workflow):
        """Adds a Swimlane instance with the provided Workflow data model object

        Args:
            workflow (Workflow): A `Workflow` data model object

        Returns:
            Workflow: A `Workflow` data model object
        """
        try:
            return self._make_request("POST", "/workflow/", json=workflow)
        except Exception as e:
            return False

    @log_exception
    def update_workflow(self, workflow):
        """Updates a Swimlane instance with the provided `Workflow` data model object

        Args:
            workflow (Workflow): A `Workflow` data model object

        Returns:
            Workflow: A `Workflow` data model object
        """
        return self._make_request("PUT", f"/workflow/{workflow['id']}", json=workflow)
