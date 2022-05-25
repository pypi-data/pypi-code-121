from __future__ import annotations
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from pydantic import PrivateAttr

from workspace_clients import (
    AssetModel,
    ContainerModel,
    WorkspaceServiceAssetsClient,
    WorkspaceServiceContainersClient,
)
from adt_clients import Granularity, AnalyticDatasetFormat, AnalyticDatasetModel

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from iqvia_e360 import E360Context


class ClientStoreAssetModel(AssetModel):
    delete_method: Optional[str] = None
    service_client: Optional[str] = None
    _assets_client: WorkspaceServiceAssetsClient = PrivateAttr(default=None)
    _e360_context: E360Context = PrivateAttr(default=None)

    @property
    def e360_context(self) -> Optional[E360Context]:
        return self._e360_context

    def set_e360_context(self, context: E360Context) -> None:
        self._e360_context = context

    @property
    def assets_client(self) -> Optional[WorkspaceServiceAssetsClient]:
        return self._assets_client

    def set_assets_client(self, client: WorkspaceServiceAssetsClient) -> None:
        self._assets_client = client

    @property
    def can_purge(self) -> bool:
        return self.e360_context and self.delete_method and self.service_client

    @classmethod
    def type_matches(cls, model: AssetModel) -> bool:
        return all(
            [
                cls.__fields__["type"].default == model.type,
                cls.__fields__["subtype"].default == model.subtype,
            ]
        )

    @classmethod
    def create(cls, model: AssetModel, store: E360Context) -> ClientStoreAssetModel:
        Klass = ClientStoreAssetModel
        for klass in ClientStoreAssetModel.__subclasses__():
            if klass.type_matches(model):
                Klass = klass
                break
        data = model.dict(exclude_none=True, by_alias=True)
        inst = Klass.parse_obj(data)
        inst.set_e360_context(store)
        inst.set_assets_client(model._client)
        return inst

    def delete(self, purge: bool = False) -> bool:
        """
        Delete service resources first, as some rely on WS assets to test access rights
        """
        cont = True
        if self.can_purge and purge and self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            cont = getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return cont and super().delete()


class AdtReportAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete"
    service_client: str = "get_adt_client"
    type: str = "Analytic Dataset"
    subtype: str = "Report"

    def download(self, location: Union[Path, str] = None) -> Path:
        return self.e360_context.download_adt_report(self, location)

    def delete(self, purge: bool = False) -> bool:
        """
        ADT will delete workspace assets when the report is deleted
        """
        if self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            return getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return True


class AdtDefinitionAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete"
    service_client: str = "get_adt_definition_client"
    type: str = "Analytic Dataset"
    subtype: str = "Definition"

    def delete(self, purge: bool = False) -> bool:
        """
        ADT will delete workspace assets when the definition is deleted
        """
        if self.metadata.get("LocalAssetId"):
            client = getattr(self.e360_context, self.service_client)()
            return getattr(client, self.delete_method)(self.metadata["LocalAssetId"])
        return True


class FileAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_fs_client"
    type: str = "Document"
    subtype: Optional[str] = None

    def delete(self, purge: bool = False) -> bool:
        cont = True
        if purge and self.metadata.get("Document/FileId"):
            client = getattr(self.e360_context, self.service_client)()
            cont = getattr(client, self.delete_method)(self.metadata["Document/FileId"])
        return cont and super().delete()


class PlotlyVisualizationAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_vrs_plotly_client"
    type: str = "Visualisation"

    @classmethod
    def type_matches(cls, model: AssetModel) -> bool:
        return all(
            [
                cls.__fields__["type"].default == model.type,
                model.metadata,
                model.metadata.get("VisType") == "Plotly",
            ]
        )


class VisualizationAssetModel(ClientStoreAssetModel):
    delete_method: str = "delete_by_id"
    service_client: str = "get_vrs_client"
    type: str = "Visualisation"

    @classmethod
    def type_matches(cls, model: AssetModel) -> bool:
        return all(
            [
                cls.__fields__["type"].default == model.type,
                model.metadata,
                model.metadata.get("VisType") == "GWAS",
            ]
        )


class ContainerAssetModel(ContainerModel):
    _containers_client: WorkspaceServiceContainersClient = PrivateAttr(default=None)
    _e360_context: E360Context = PrivateAttr(default=None)

    @property
    def e360_context(self) -> Optional[E360Context]:
        return self._e360_context

    def set_e360_context(self, context: E360Context) -> None:
        self._e360_context = context

    @property
    def containers_client(self) -> Optional[WorkspaceServiceContainersClient]:
        return self._containers_client

    def set_containers_client(self, client: WorkspaceServiceContainersClient) -> None:
        self._containers_client = client

    def upload_adt_file(
        self,
        file_path: Union[Path, str],
        name: str,
        granularity: Granularity,
        format_: AnalyticDatasetFormat,
        dataset_release_id: str = None,
    ) -> AnalyticDatasetModel:
        return self.e360_context.upload_adt_file(
            self, file_path, name, granularity, format_, dataset_release_id
        )

    def create_child_container(
        self, name: str, description: str = ""
    ) -> ContainerAssetModel:
        return self.e360_context.create_workspace_container(self.id, name, description)

    def upload_document(
        self, file_path: Union[Path, str], name: str, description: str = ""
    ) -> AssetModel:
        return self.e360_context.upload_document_file(
            self, file_path, name, description
        )
