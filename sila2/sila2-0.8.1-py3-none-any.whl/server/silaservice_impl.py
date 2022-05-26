from __future__ import annotations

from typing import TYPE_CHECKING, List

from sila2.features.silaservice import SiLAServiceBase, UnimplementedFeature
from sila2.server.metadata_dict import MetadataDict

if TYPE_CHECKING:
    from sila2.server.sila_server import SilaServer


class SiLAServiceImpl(SiLAServiceBase):
    def __init__(self, parent_server: SilaServer):
        super().__init__(parent_server=parent_server)

    def GetFeatureDefinition(self, FeatureIdentifier: str, *, metadata: MetadataDict) -> str:
        if FeatureIdentifier not in (f.fully_qualified_identifier for f in self.parent_server.features.values()):
            raise UnimplementedFeature(f"Feature {FeatureIdentifier} is not implemented by this server")

        return self.parent_server.features[FeatureIdentifier.split("/")[-2]]._feature_definition

    def SetServerName(self, ServerName: str, *, metadata: MetadataDict) -> None:
        self.parent_server.server_name = ServerName

    def get_ImplementedFeatures(self, *, metadata: MetadataDict) -> List[str]:
        return [f.fully_qualified_identifier for f in self.parent_server.features.values()]

    def get_ServerName(self, *, metadata: MetadataDict) -> str:
        return self.parent_server.server_name

    def get_ServerType(self, *, metadata: MetadataDict) -> str:
        return self.parent_server.server_type

    def get_ServerUUID(self, *, metadata: MetadataDict) -> str:
        return str(self.parent_server.server_uuid)

    def get_ServerDescription(self, *, metadata: MetadataDict) -> str:
        return self.parent_server.server_description

    def get_ServerVersion(self, *, metadata: MetadataDict) -> str:
        return self.parent_server.server_version

    def get_ServerVendorURL(self, *, metadata: MetadataDict) -> str:
        return self.parent_server.server_vendor_url
