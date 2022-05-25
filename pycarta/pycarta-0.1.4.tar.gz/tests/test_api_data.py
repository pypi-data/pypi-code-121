import json
import pytest
import logging

from pycarta.graph.node import Node
from pycarta.api.data import get_sources
from pycarta.api.data import get_resources
from pycarta.api.data import (
    get_data,
    get_roots,
    get_children,
    get_descendants,
    get_ids,
    post_graph,
    delete_resource
)

from .common_fixtures import agent, cartaAuth, cartaUrl


@pytest.fixture
def expected_sources():
    with open("expected_output.json", "rb") as ifs:
        return json.load(ifs)["api"]["sources"]

@pytest.fixture
def expected_resources():
    with open("expected_output.json", "rb") as ifs:
        return json.load(ifs)["api"]["synthetic resources"]

@pytest.fixture
def infinite_directed_graph_roots(agent):
    return get_data(
        agent,
        "synthetic",
        "InfiniteDirectedGraph",
        verify=False
    )

@pytest.fixture
def infinite_directed_graph_root_0_children(
    agent,
    infinite_directed_graph_roots
):
    rootId = TestGetData.get_root_id(infinite_directed_graph_roots)
    return get_data(
        agent,
        "synthetic",
        "InfiniteDirectedGraph",
        selector="children",
        params={
            "ids": rootId
        },
        verify=False
    )

def synthetic_graph():
    """
    Creates the nodes and edges of a fully connected, acyclic graph.
    """
    import os
    import numpy as np

    def make_property(name, domain=(-10, 10)):
        """Create a property from a name."""
        lo, hi = domain
        span = hi-lo
        return Node.Property(id=name, values=span*np.random.random() + lo)

    def make_node(label, properties=None):
        """Create a node from a label."""
        if properties is None:
            properties = np.random.choice(
                props,
                size=np.random.randint(5),
                replace=False
            )
        return Node(
            label,
            properties=[make_property(k) for k in properties]
        )

    def grow(root, splits, depth=0):
        """
        Grow a graph recursively to `depth` with `splits` children per node.
        """
        nodes = [root]
        if depth <= 0:
            return (nodes, [])
        children = [
            make_node(label) for label in np.random.choice(words, size=splits)
        ]
        edges = [(root, child) for child in children]
        for child in children:
            n, e = grow(
                child,
                splits=np.random.randint(2, 4+1),
                depth=depth-np.random.randint(1, 3)
            )
            nodes.extend(n)
            edges.extend(e)
        return (nodes, edges)

    # get a big list of words.
    logger = logging.getLogger()
    wordsFile = "/usr/share/dict/words"
    if os.path.isfile(wordsFile):
        logger.debug("pytest::Reading words from %s", wordsFile)
        with open(wordsFile) as ifs:
            words = ifs.read().splitlines() # grow depends on this
    else:
        # create random 3-6 letter words
        logger.debug("pytest::Generating random 3-6 letter words.")
        words = [
            w[:n] for n,w in zip(
                np.random.randint(3, 6+1, size=250000),
                np.random.choice(
                    [chr(i) for i in range(ord('a'), ord('z')+1)],
                    size=(250000, 6)
                )
            )
        ]
    props = np.random.choice(words, size=15) # make_node depends on this
    return grow(
        make_node(np.random.choice(words)),
        splits=np.random.randint(2, 4+1),
        depth=np.random.randint(2, 6)
    )


def test_get_sources(agent, expected_sources):
    response = get_sources(agent, verify=False)
    assert response == expected_sources


def test_get_resources(agent, expected_resources):
    response = get_resources(agent, "synthetic", verify=False)
    assert response == expected_resources
    # Test failure when attempting to access and invalid source
    response = get_resources(agent, "invalid", verify=False)
    assert response is None


class TestGetData:
    @staticmethod
    def get_root(roots):
        return roots["nodes"]

    @staticmethod
    def get_root_id(roots):
        return roots["nodes"][0]["id"]

    def test_roots(self, agent, infinite_directed_graph_roots):
        # valid response
        response = infinite_directed_graph_roots
        assert response is not None
        # synonym
        other = get_roots(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            verify=False
        )
        assert response == other

    def test_children(
        self,
        agent,
        infinite_directed_graph_roots,
        infinite_directed_graph_root_0_children
    ):
        response = infinite_directed_graph_root_0_children
        assert response is not None
        # test equivalent function call
        rootID=TestGetData.get_root_id(infinite_directed_graph_roots)
        other = get_children(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            ids=rootID,
            verify=False
        )
        assert response == other

    def test_include(self, agent, infinite_directed_graph_roots):
        roots = TestGetData.get_root(infinite_directed_graph_roots)
        rootId = TestGetData.get_root_id(infinite_directed_graph_roots)
        response = get_data(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            selector="include",
            params={
                "ids": rootId
            },
            verify=False
        )
        # Create a sorted list of node IDs.
        actual = tuple(sorted([n["id"] for n in response["nodes"]]))
        expected = tuple(sorted([n["id"] for n in roots]))
        assert actual == expected
        # test other approach
        rootID=TestGetData.get_root_id(infinite_directed_graph_roots)
        other = get_ids(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            ids=rootID,
            verify=False
        )
        assert response == other

    def test_descendants(
        self,
        agent,
        infinite_directed_graph_roots,
        infinite_directed_graph_root_0_children
    ):
        roots = TestGetData.get_root(infinite_directed_graph_roots)
        children = infinite_directed_graph_root_0_children
        rootId = TestGetData.get_root_id(infinite_directed_graph_roots)
        response = get_data(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            selector="descendants",
            params={
                "ids": rootId,
                "depth": 1,
                "includeRoots": False
            },
            verify=False
        )
        # Create a sorted list of node IDs.
        actual = tuple(sorted([n["id"] for n in response["nodes"]]))
        expected = tuple(sorted([n["id"] for n in children["nodes"]]))
        assert actual == expected
        # test equivalent/specialized call
        other = get_descendants(
            agent,
            "synthetic",
            "InfiniteDirectedGraph",
            ids=rootId,
            depth=1,
            includeRoots=False,
            verify=False
        )
        assert response == other


class TestPostData:
    def test_post_graph(self, agent):
        import numpy as np
        rng = np.random.default_rng()
        nodes, edges = synthetic_graph()
        # delete existing user resources
        source = "user"
        resources = get_resources(agent, source, verify=False)
        for resource in resources:
            delete_resource(agent, source, resource, verify=False)
        # generate new graphs
        response = post_graph(
            agent,
            source,
            label="TestPostData::test_post_graph",
            nodes=nodes,
            verify=False
        )
        assert response, "Failed to post graph from nodes"
        response = post_graph(
            agent,
            source,
            label="TestPostData::test_post_graph",
            edges=edges,
            verify=False
        )
        assert response, "Failed to post graph from edges"
        response = post_graph(
            agent,
            source,
            label="TestPostData::test_post_graph",
            nodes=rng.choice(nodes, size=len(nodes)//2),
            edges=rng.choice(edges, size=len(edges)//2),
            verify=False
        )
        assert response, "Failed to post graph from nodes and edges."
