import os
import s3fs
import networkx as nx
import pandas as pd
import deepstruct.dataset as dds

from joblib import Parallel, delayed
from typing import Sequence, Union

from ctnas.themes import is_isomorphic_theme


class CTNASApiError(BaseException):
    pass


class CTNASApi(object):
    def __init__(self, access_key: str = None, secret_key: str = None, endpoint: str = None, path_cache: str = "~/.cache/ctnas/"):
        path_cache = os.path.expanduser(path_cache)
        if not os.path.exists(path_cache):
            os.makedirs(path_cache)
        self._path_cache = path_cache

        self._s3_access_key = access_key if access_key is not None else "ctnas-public-acc"
        self._s3_secret_key = secret_key if secret_key is not None else "ctnas-public-sec"
        self._s3_endpoint = endpoint if endpoint is not None else "https://share.pads.fim.uni-passau.de"
        self._s3_base = "/homes/stier/ctnas/"

        self._pd_graph_props = None
        self._pd_computations = None

        self._initialize_s3fs()

    def _initialize_s3fs(self):
        self._s3fs = s3fs.S3FileSystem(
            key=self._s3_access_key,
            secret=self._s3_secret_key,
            use_ssl=True,
            client_kwargs={
              "endpoint_url": self._s3_endpoint,
            }
        )

    def _ensure_pd_graph_props(self):
        if self._pd_graph_props is None:
            self._load_pd_graph_props()

    def _load_pd_graph_props(self):
        path_cache_propfile = os.path.join(self._path_cache, "graph-properties.csv")
        path_s3_propfile = os.path.join(self._s3_base, "graph-properties.csv")
        if not os.path.exists(path_cache_propfile):
            self._s3fs.download(path_s3_propfile, path_cache_propfile)

        self._pd_graph_props = pd.read_csv(path_cache_propfile)

    def _ensure_pd_computations(self):
        if self._pd_computations is None:
            self._load_pd_computations()

    def _load_pd_computations(self):
        path_cache_compfile = os.path.join(self._path_cache, "ctnas-computations.csv")
        path_s3_compfile = os.path.join(self._s3_base, "ctnas-computations.csv")
        if not os.path.exists(path_cache_compfile):
            self._s3fs.download(path_s3_compfile, path_cache_compfile)

        self._pd_computations = pd.read_csv(path_cache_compfile)

    def _get_functional_data(self, name_full_qualified: str) -> dds.FuncDataset:
        path_cache_fds = os.path.join(self._path_cache, "fds", name_full_qualified + ".fds")
        path_s3_fds = os.path.join(self._s3_base, "fds", name_full_qualified + ".fds")
        if not os.path.exists(path_cache_fds):
            try:
                self._s3fs.download(path_s3_fds, path_cache_fds)
            except FileNotFoundError as e:
                raise CTNASApiError(f"Could not find dataset for FuncDataset with qualifier '{name_full_qualified}'", e)

        return dds.FuncDataset.load(path_cache_fds)

    def get_all_computations(self) -> pd.DataFrame:
        self._ensure_pd_computations()
        return self._pd_computations

    def get_all_graph_properties(self) -> pd.DataFrame:
        self._ensure_pd_graph_props()
        return self._pd_graph_props

    def get_computations(self, graph_uuid: Union[str, Sequence[str]], dataset: Union[str, Sequence[str]] = None):
        self._ensure_pd_computations()

        if not isinstance(graph_uuid, list):
            graph_uuid = [graph_uuid]

        df = self._pd_computations
        if dataset is not None:
            if not isinstance(dataset, list):
                dataset = [dataset]
            df = df[df["dataset"].isin(dataset)]

        return df[df["graph_theme"].isin(graph_uuid)]

    def find_by_graph(self, graphs: Union[nx.DiGraph, Sequence[nx.DiGraph]]) -> Sequence[str]:
        if not isinstance(graphs, list):
            graphs = [graphs]

        assert all(isinstance(graph, nx.DiGraph) for graph in graphs), "Requiring a directed graph type"

        def check_isomorphic(graphs_ref, uuid_other):
            graph_other = self.get_graph(uuid_other)
            for graph_ref in graphs_ref:
                if is_isomorphic_theme(graph_ref, graph_other):
                    return uuid_other
            return None
        return [found_uuid for found_uuid in Parallel(n_jobs=4)(delayed(check_isomorphic)(graphs, other_uuid) for other_uuid in self.get_graph_uuids()) if found_uuid is not None]

    def get_graph(self, uuid: str) -> nx.Graph:
        path_cache_graph = os.path.join(self._path_cache, "graphs", uuid + ".adjlist")
        path_s3_graph = os.path.join(self._s3_base, "graphs", uuid + ".adjlist")
        if not os.path.exists(path_cache_graph):
            try:
                self._s3fs.download(path_s3_graph, path_cache_graph)
            except FileNotFoundError as e:
                raise CTNASApiError("Could not find graph with that UUID=%s" % uuid, e)

        return nx.read_adjlist(path_cache_graph, create_using=nx.DiGraph)

    def get_graphs(self, uuid_refs: Sequence[str] = None, return_uuid: bool = False) -> Sequence[nx.Graph]:
        if uuid_refs is None:
            uuid_refs = self.get_graph_uuids()
        for uuid in uuid_refs:
            yield self.get_graph(uuid) if not return_uuid else uuid, self.get_graph(uuid)

    def get_graph_uuids(self) -> Sequence[str]:
        self._ensure_pd_graph_props()
        return list(pd.unique(self._pd_graph_props["graph_uuid"]))

    def get_dataset_names(self) -> Sequence[str]:
        self._ensure_pd_computations()
        return list(pd.unique(self._pd_computations["dataset"]))

    def get_dataset(self, name_dataset: str) -> dds.FuncDataset:
        map_name_to_full_qualifier = {
            "spheres-b8c16fd7": "dataset-spheres-c10-s2-n20000-sr10-lr10-lb-100-ub100-b8c16fd7-3562-48e0-a100-ce57610839df",
            "spheres-23aeba4d": "dataset-spheres-c10-s2-n20000-sr10-lr20-lb-100-ub100-23aeba4d-1407-403a-95d5-a4e7bb391586",
            "spheres-bee36cd9": "dataset-spheres-c10-s2-n20000-sr10-lr10-lb-100-ub100-bee36cd9-c4f4-47e0-9594-68e62c04e430",
            "spheres-b758e9f4": "dataset-spheres-c10-s3-n20000-sr10-lr20-lb-100-ub100-b758e9f4-3f73-4924-b621-c465e67bc075",
            "spheres-0a19afe4": "dataset-spheres-c10-s3-n20000-sr10-lr10-lb-100-ub100-0a19afe4-a400-4444-8259-38c420baaac3",
            "spheres-6598864b": "dataset-spheres-c10-s3-n20000-sr10-lr10-lb-100-ub100-6598864b-2617-485d-b59c-174bbe4761ea"
        }

        if name_dataset in map_name_to_full_qualifier:
            name_dataset = map_name_to_full_qualifier[name_dataset]

        return self._get_functional_data(name_dataset)
