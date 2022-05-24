import os
from pathlib import Path
from typing import Optional, Union

import tableauserverclient as TSC


class MultipleProjectsShareNameException(Exception):
    def __init__(self, name_shared, projects: Optional[list[TSC.ProjectItem]] = None):
        messages: list[str] = [
            f'Multiple projects share the name "{name_shared}",',
            "try providing a project name including parent projects separated by '/'",
            "or try referencing using the id of the project instead:",
        ]
        if projects is not None:
            project_descs = [
                f"  name: {x.name}; id: {x.id}; desc: {x.description}" for x in projects
            ]
            messages.extend(project_descs)

        message = "\n".join(messages)
        super().__init__(message)


class ProjectNotFoundException(Exception):
    def __init__(self, name_or_id):
        message = f'No project was found with the given name or id: "{name_or_id}",'
        super().__init__(message)


class ServerHelper:
    def __init__(
        self,
        tableau_server_url: Optional[str] = None,
        tableau_api_version: Optional[str] = None,
        verify: Union[bool, Path] = True,
        token_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
    ):
        self.server: TSC = ServerHelper._open_connection(
            tableau_server_url=tableau_server_url,
            tableau_api_version=tableau_api_version,
            verify=verify,
            token_name=token_name,
            personal_access_token=personal_access_token,
        )

    @staticmethod
    def _open_connection(
        tableau_server_url: Optional[str] = None,
        tableau_api_version: Optional[str] = None,
        verify: Union[bool, Path] = True,
        token_name: Optional[str] = None,
        personal_access_token: Optional[str] = None,
    ):
        if tableau_server_url is None:
            tableau_server_url = os.getenv("TABLEAU_SERVER_URL")
        if token_name is None:
            token_name = os.getenv("TABLEAU_TOKEN_NAME")
        if personal_access_token is None:
            personal_access_token = os.getenv("TABLEAU_PERSONAL_ACCESS_TOKEN")

        tableau_ssl_cert = os.getenv("TABLEAU_SSL_CERT_PATH", None)
        if tableau_ssl_cert is not None and verify is True:
            verify = Path(tableau_ssl_cert)

        server = TSC.Server(tableau_server_url)

        if isinstance(verify, Path):
            server.add_http_options({"verify": str(verify)})
        server.use_server_version()
        if tableau_api_version is None:
            tableau_api_version = os.getenv("TABLEAU_API_VERSION", None)
        if tableau_api_version is not None:
            server.version = tableau_api_version

        auth = TSC.PersonalAccessTokenAuth(
            token_name=token_name,
            personal_access_token=personal_access_token,
            site_id="",
        )
        server.auth.sign_in_with_personal_access_token(auth)
        return server

    def get_project_id(
        self,
        project_name: str,
        parent_id: Optional[str] = None,
    ) -> str:
        server = self.server
        projects: list[TSC.ProjectItem]
        projects, _ = server.projects.get()
        project_name_remainder = None
        if project_name.find("/") > 0:
            project_name_parts = project_name.split("/", 1)
            project_name = project_name_parts[0]
            project_name_remainder = project_name_parts[1]
        projects_filtered = [x for x in projects if x.name == project_name]
        if parent_id is not None:
            projects_filtered = [
                x for x in projects_filtered if x.parent_id == parent_id
            ]
        # it isn't clear if tableau can return multiple projects with the same name
        # we should avoid unintentional writing to the wrong project
        if len(projects_filtered) > 1:
            raise MultipleProjectsShareNameException(project_name, projects_filtered)
        elif len(projects_filtered) < 1:
            # try finding a matching id instead of name as a backup
            projects_filtered = [x for x in projects if x.id == project_name]

        if len(projects_filtered) < 1:
            raise ProjectNotFoundException(project_name)

        project_id = projects_filtered[0].id
        if project_name_remainder is None:
            return project_id

        return self.get_project_id(project_name_remainder, project_id)

    def get_flow(self, project_name, flow_name) -> Optional[TSC.FlowItem]:
        project_id: str = self.get_project_id(project_name)
        flows: list[TSC.FlowItem]
        flows, _ = self.server.flows.get()
        for flow in flows:
            if flow.project_id == project_id and flow.name == flow_name:
                return flow
        return None

    def create_or_replace_hyper_file(
        self,
        source: Path,
        dest_project: str,
        name: Optional[str] = None,
    ):
        """

        :param source: the hyperfile to be uploaded
        :param dest_project: the project name, path, or id
        :param name: optionally set a different name from the filename
        :return: None
        """  # noqa
        project_id = self.get_project_id(
            project_name=dest_project,
        )
        server = self.server
        publish_mode = TSC.Server.PublishMode.Overwrite
        datasource = TSC.DatasourceItem(project_id, name=name)
        server.datasources.publish(datasource, source, publish_mode)


def get_project_id(
    project_name: str,
    parent_id: Optional[str] = None,
    tableau_server_url: Optional[str] = None,
    verify: Union[bool, Path] = True,
    token_name: Optional[str] = None,
    personal_access_token: Optional[str] = None,
) -> str:
    helper = ServerHelper(
        tableau_server_url=tableau_server_url,
        verify=verify,
        token_name=token_name,
        personal_access_token=personal_access_token,
    )
    return helper.get_project_id(project_name=project_name, parent_id=parent_id)


def create_or_replace_hyper_file(
    hyperfile_path: Path,
    project: str,
    name: Optional[str] = None,
    tableau_server_url: Optional[str] = None,
    verify: Union[bool, Path] = True,
    token_name: Optional[str] = None,
    personal_access_token: Optional[str] = None,
):
    """

    :param hyperfile_path: the hyperfile to be uploaded
    :param project: the project name or id
    :param name: optionally set a different name from the filename
    :param tableau_server_url: the full url to your tableau_server (https://...), when None the ENVVAR "TABLEAU_SERVER_URL" will be loaded
    :param verify: optionally disable ssl or point to a trusted cert path
    :param token_name: the name of your PAC, when None the ENVVAR "TABLEAU_TOKEN_NAME" will be loaded
    :param personal_access_token: the value of your PAC, when None the ENVVAR "TABLEAU_PERSONAL_ACCESS_TOKEN" will be loaded
    :return: None
    """  # noqa
    helper = ServerHelper(
        tableau_server_url=tableau_server_url,
        verify=verify,
        token_name=token_name,
        personal_access_token=personal_access_token,
    )
    helper.create_or_replace_hyper_file(
        source=hyperfile_path,
        dest_project=project,
        name=name,
    )
