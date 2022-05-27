import json
import posixpath
from urllib.parse import quote_plus
from typing import Type, Optional

from openlineage.client import OpenLineageClientOptions

from tokyo_annotation.models.node import Node
from tokyo_annotation.adapter import OpenLineageClientFacade
from tokyo_annotation.utils.lineage import (
    Lineage,
    parse_raw_lineage,
    get_genesis_datasets
)


BASE_ENDPOINT = 'api/v1'


class Facade:
    def __init__(
        self,
        namespace: str,
        dataset_name: str,
        openlineage_client: OpenLineageClientFacade
    ) -> None:
        self.node_id = f'dataset:{namespace}:{dataset_name}'
        
        self.openlineage_client = openlineage_client

        raw_lineage = self._get_raw_lineage(openlineage_client)
        self.lineage: Lineage = parse_raw_lineage(raw_lineage)
        self.node: Type[Node] = None

        for _, node in self.lineage.graph.nodes.map.items():
            if node.id == self.node_id:
                self.node = node

    def get(self):
        genesis = self._get_genesis_datasets()

        annotations = {}

        for node in genesis:
            if node.type == 'DATASET':
                annotation = self._get_annotation(node)
                if annotation:
                    annotations[node.id] = annotation
        
        return annotations

    @classmethod
    def from_openlineage_url(
        cls,
        namespace: str,
        dataset_name: str,
        openlineage_url: str,
        openlineage_client_options: Optional[OpenLineageClientOptions] \
                                        = OpenLineageClientOptions()
    ):
        openlineage_client = OpenLineageClientFacade.from_url(
                                openlineage_url, openlineage_client_options)
        
        return cls(namespace, dataset_name, openlineage_client)
    
    def _get_raw_lineage(
        self,
        openlineage_client: OpenLineageClientFacade
    ):
        adapter = openlineage_client

        raw_lineage = adapter.get(
            path=posixpath.join(BASE_ENDPOINT, 'lineage'),
            params={
            "nodeId": self.node_id
        })

        return raw_lineage.text
    
    def _get_genesis_datasets(self):
        if not self.node:
            return
        
        return get_genesis_datasets(self.node, self.lineage)
    
    def _get_annotation(
        self,
        node: Type[Node]):
        adapter = self.openlineage_client

        namespace = quote_plus(node.meta['namespace'])
        dataset_name = quote_plus(node.meta['name'])
        path = f'namespaces/{namespace}/datasets/{dataset_name}'

        metadata = adapter.get(
            path=posixpath.join(BASE_ENDPOINT, path)
        )

        metadata = json.loads(metadata.text)

        if 'facets' in metadata:
            if 'annotation' in metadata['facets']:
                return metadata['facets']['annotation']
        
        return None