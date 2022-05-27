# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.¨

from typing import Sequence
from google.protobuf.any_pb2 import Any

from . import logger
from .client import HubClient
from .base_ctx import BaseContext
from .connector_filter import ConnectorFilter
from .petrel_pb2 import ProjectInfoRequest, ProjectInfoResult
from .petrel_pb2 import PoisonPetrelRequest, PoisonPetrelResult
from .petrel_pb2 import LoadProjectRequest, LoadProjectResult
from .petrel_pb2 import NewProjectRequest, NewProjectResult
from .petrel_pb2 import SaveProjectRequest, SaveProjectResult
from .petrel_pb2 import SaveAsProjectRequest, SaveAsProjectResult
from .petrel_pb2 import CloseProjectRequest, CloseProjectResult


class PetrelContext(BaseContext):
    """A context or handle to a Cegal Hub Petrel Connector(s). Connectors may be targted by providing a ConnectorFilter"""

    def __init__(self, hub_client: HubClient, wellknown_connector_id: str, connector_filter: ConnectorFilter = None):
        """Creates a PetrelContext from the specified parameters.

        Args:
            hub_client (HubClient): The HubClient which makes client requests to Cegal Hub Server.
            wellknown_connector_id (str): The wellknown string that represents the type of connector. i.e cegal.hub.petrel or cegal.hub.agent etc
            connector_filter (ConnectorFilter, optional): A Connector filter to target a specific instance or instances of a Connector. Defaults to None.
        """
        super().__init__(hub_client, wellknown_connector_id, connector_filter)

    def project_info(self, use_ref_project: bool = False):
        """Summary information of the Petrel project.

        Args:
            use_ref_project (bool, optional): If True use the secondary project loaded in Petrel(if available), otherwise use the primary project. Defaults to False.

        Raises:
            Exception: If there was a problem obtaining the Petrel project information

        Returns:
            ProjectInfoResult: An object containing the Petrel project information.
        """        
        msg = ProjectInfoRequest()
        msg.use_ref_project = use_ref_project
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_info", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = ProjectInfoResult()
            result.Unpack(response)
            logger.info(f"got project info:{response} on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to get Petrel project info: {result} on connector_id {connector_id}")
            raise Exception(f"failed to get Petrel project info: {result} on connector_id {connector_id}")

    def poison_petrel(self):
        """Kill the running instance of Petrel

        Raises:
            Exception: If there was a problem trying to kill Petrel

        Returns:
            PoisonPetrelResult: An object representing the result of attempting to kill Petrel
        """        
        msg = PoisonPetrelRequest()
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.poison_petrel", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = PoisonPetrelResult()
            result.Unpack(response)
            logger.info(f"Petrel has been killed on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to kill Petrel: {result} on connector_id {connector_id}")
            raise Exception(f"failed to kill Petrel: {result} on connector_id {connector_id}")

    def load_project(self, path: str, read_only: bool = True, use_ref_project: bool = False):
        """Load a Petrel project into the running instance of Petrel

        Args:
            path (str): The path to .pet Petrel project file
            read_only (bool, optional): True if the project should be opened in readonly mode. Defaults to True.
            use_ref_project (bool, optional): True if the project should be opened as a secondary project in Petrel. Defaults to False.

        Raises:
            Exception: If there was a problem loading the Petrel project

        Returns:
            LoadProjectResult: An object representing the result of loading a Petrel project
        """        
        msg = LoadProjectRequest()
        msg.path = path
        msg.read_only = read_only
        msg.use_ref_project = use_ref_project
        payload = Any()
        payload.Pack(msg)
        logger.info("loading Petrel project, this could take a while...")
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_load", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = LoadProjectResult()
            result.Unpack(response)
            logger.info(f"project successfully loaded: {response} on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to load  project: {result} on connector_id {connector_id}")
            raise Exception(f"failed to load  project: {result} on connector_id {connector_id}")

    def new_project(self):
        """Create a new project in the running instance of Petrel.

        Raises:
            Exception: If there was a problem creating the new Petrel project.

        Returns:
            NewProjectResult: An object representing the result of creating a new Petrel project.
        """        
        msg = NewProjectRequest()
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_new", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = NewProjectResult()
            result.Unpack(response)
            logger.info(f"new project successfully created: {result} on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to create new project: {result} on connector_id {connector_id}")
            raise Exception(f"failed to create new project: {result} on connector_id {connector_id}")

    def save_project(self, use_ref_project: bool = False, allow_project_version_upgrade: bool = False):
        """Save the Petrel project.

        Args:
            use_ref_project (bool, optional): If True save the secondary petrel project, otherwise save the primary Petrel project. Defaults to False.
            allow_project_version_upgrade (bool, optional): If True allow Petrel to save the project in a newer version of Petrel otherwise fail
            if this scenario is encountered. Defaults to False.

        Raises:
            Exception: If there was a problem saving the Petrel project.

        Returns:
            SaveProjectResult: An object representing the result of saving the Petrel project.
        """        
        msg = SaveProjectRequest()
        msg.use_ref_project = use_ref_project
        msg.allow_project_version_upgrade = allow_project_version_upgrade
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_save", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = SaveProjectResult()
            result.Unpack(response)
            logger.info(f"project successfully saved {result} on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to save project: {result} on connector_id {connector_id}")
            raise Exception(f"failed to save project: {result} on connector_id {connector_id}")

    def save_as_project(self, path: str, use_ref_project: bool = False):
        """Perform a save as on the running Petrel project.

        Args:
            path (str): The path including the name of the project for the save as
            use_ref_project (bool, optional): If True perform save as on the secondary Petrel project, otherwise perform save as on the primary Petrel project. Defaults to False.

        Raises:
            Exception: It there was a problem performing the save as

        Returns:
            SaveAsProjectResult: An object representing the result of performing a save as.
        """        
        msg = SaveAsProjectRequest()
        msg.path = path
        msg.use_ref_project = use_ref_project
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_save_as", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = SaveAsProjectResult()
            result.Unpack(response)
            logger.info(f"project save as succesful on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to save as project: {result} on connector_id {connector_id}")
            raise Exception(f"failed to save as project: {result} on connector_id {connector_id}")

    def close_project(self, use_ref_project: bool = False, close_both_projects: bool = False):
        """Close the Petrel project in the running Petrel instance.

        Args:
            use_ref_project (bool, optional): If True close the secondary Petrel project otherwise close the primary Petrel project. Defaults to False.
            close_both_projects (bool, optional): If True close both the primary and secondary Petrel projects. Defaults to False.

        Raises:
            Exception: If there was a problem closing the Petrel project.

        Returns:
            CloseProjectResult: An object representing the result of closing the Petrel project.
        """        
        msg = CloseProjectRequest()
        msg.use_ref_project = use_ref_project
        msg.close_both_projects = close_both_projects
        payload = Any()
        payload.Pack(msg)
        ok, result, connector_id = self._hub_client.do_unary_request("cegal.hub.petrel", "cegal.hub.petrel.project_close", payload, connector_filter=self.connector_filter, major_version=1,minor_version=0)
        if (ok):
            response = CloseProjectResult()
            result.Unpack(response)
            logger.info(f"project(s) closed ok: {result} on connector_id {connector_id}")
            return response
        else:
            logger.warn(f"failed to close project(s): {result} on connector_id {connector_id}")
            raise Exception(f"failed to close project(s): {result} on connector_id {connector_id}")
