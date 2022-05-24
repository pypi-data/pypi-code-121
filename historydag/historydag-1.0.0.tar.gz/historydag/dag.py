"""A module providing the class HistoryDag, and supporting functions."""

import pickle
import graphviz as gv
import ete3
import random
from typing import (
    List,
    Callable,
    Any,
    Mapping,
    Generator,
    Iterable,
    Set,
    Optional,
    Tuple,
    NamedTuple,
    Dict,
    FrozenSet,
    Union,
    Sequence,
)
from collections import Counter
from copy import deepcopy

from historydag import utils
from historydag.utils import Weight, Label, UALabel, prod
from historydag.counterops import counter_sum, counter_prod


class HistoryDagNode:
    r"""A recursive representation of a history DAG object
    - a dictionary keyed by clades (frozensets) containing EdgeSet objects
    - a label, which is a namedtuple.
    """

    def __init__(self, label: Label, clades: dict, attr: Any):
        self.clades = clades
        # If passed a nonempty dictionary, need to add self to children's parents
        self.label = label
        self.parents: Set[HistoryDagNode] = set()
        self.attr = attr
        self._dp_data: Any = None
        if self.clades:
            for _, edgeset in self.clades.items():
                edgeset.parent = self
            for child in self.children():
                child.parents.add(self)

        if len(self.clades) == 1:
            raise ValueError(
                "Internal nodes (those which are not the DAG UA root node) "
                "may not have exactly one child clade; Unifurcations cannot be expressed "
                "in the history DAG."
            )

    def __repr__(self) -> str:
        return str((self.label, set(self.clades.keys())))

    def __hash__(self) -> int:
        return hash((self.label, self.partitions()))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, HistoryDagNode):
            return (self.label, self.partitions()) == (other.label, other.partitions())
        else:
            raise NotImplementedError

    def node_self(self) -> "HistoryDagNode":
        """Returns a HistoryDagNode object with the same clades and label, but
        no descendant edges."""
        return HistoryDagNode(
            self.label, {clade: EdgeSet() for clade in self.clades}, deepcopy(self.attr)
        )

    def under_clade(self) -> FrozenSet[Label]:
        r"""Returns the union of this node's child clades"""
        if self.is_leaf():
            return frozenset([self.label])
        else:
            return frozenset().union(*self.clades.keys())

    def is_leaf(self) -> bool:
        """Returns whether this is a leaf node."""
        return not bool(self.clades)

    def is_root(self) -> bool:
        """Returns whether this is a DAG root node, or UA (universal ancestor)
        node."""
        return False

    def partitions(self) -> frozenset:
        """Returns the node's child clades, or a frozenset containing a
        frozenset if this node is a UANode."""
        return frozenset(self.clades.keys())

    def children(
        self, clade: Set[Label] = None
    ) -> Generator["HistoryDagNode", None, None]:
        r"""Returns generator object containing child nodes.

        Args:
            clade: If clade is provided, returns generator object of edge targets from that
        clade. If no clade is provided, generator includes all children of self.
        """
        if clade is None:
            return (
                target for clade in self.clades for target, _, _ in self.clades[clade]
            )
        else:
            return (child for child, _, _ in self.clades[clade])

    def add_edge(
        self,
        target: "HistoryDagNode",
        weight: Weight = 0,
        prob: float = None,
        prob_norm: bool = True,
    ) -> bool:
        r"""Adds edge, if allowed and not already present. Returns whether edge was added."""
        # target clades must union to a clade of self
        key = frozenset() if self.is_root() else target.under_clade()
        if key not in self.clades:
            raise KeyError("Target clades' union is not a clade of this parent node: ")
        else:
            target.parents.add(self)
            return self.clades[key].add_to_edgeset(
                target,
                weight=weight,
                prob=prob,
                prob_norm=prob_norm,
            )

    def _get_subtree_by_subid(self, subid: int) -> "HistoryDagNode":
        r"""Returns the subtree below the current HistoryDagNode corresponding to the given index"""
        if self.is_leaf():  # base case - the node is a leaf
            return self
        else:
            history = self.node_self()

            # get the subtree for each of the clades
            for clade, eset in self.clades.items():
                # get the sum of subtrees of the edges for this clade
                num_subtrees = 0  # is this the right way to get the number of edges?
                for child, weight, _ in eset:
                    num_subtrees = num_subtrees + child._dp_data
                curr_index = subid % num_subtrees

                # find the edge corresponding to the curr_index
                for child, weight, _ in eset:
                    if curr_index >= child._dp_data:
                        curr_index = curr_index - child._dp_data
                    else:
                        # add this edge to the tree somehow
                        history.clades[clade].add_to_edgeset(
                            child._get_subtree_by_subid(curr_index)
                        )
                        break

                subid = subid / num_subtrees
        return history

    def remove_edge_by_clade_and_id(self, target: "HistoryDagNode", clade: frozenset):
        key: frozenset
        if self.is_root():
            key = frozenset()
        else:
            key = clade
        self.clades[key].remove_from_edgeset_byid(target)

    def remove_node(self, nodedict: Dict["HistoryDagNode", "HistoryDagNode"] = {}):
        r"""Recursively removes node self and any orphaned children from dag.
        May not work on root.
        Does not check to make sure that parent clade still has descendant edges."""
        if self in nodedict:
            nodedict.pop(self)
        for child in self.children():
            if self in child.parents:
                child.parents.remove(self)
            if not child.parents:
                child.remove_node(nodedict=nodedict)
        for parent in self.parents:
            parent.remove_edge_by_clade_and_id(self, self.under_clade())
        self.removed = True

    def _sample(self) -> "HistoryDagNode":
        r"""Samples a clade tree (a sub-history DAG containing the root and all
        leaf nodes). Returns a new HistoryDagNode object."""
        sample = self.node_self()
        for clade, eset in self.clades.items():
            sampled_target, target_weight = eset.sample()
            sample.clades[clade].add_to_edgeset(
                sampled_target._sample(),
                weight=target_weight,
            )
        return sample

    def _get_trees(self) -> Generator["HistoryDagNode", None, None]:
        r"""Return a generator to iterate through all trees expressed by the DAG."""

        def genexp_func(clade):
            # Return generator expression of all possible choices of tree
            # structure from dag below clade
            def f():
                eset = self.clades[clade]
                return (
                    (clade, targettree, i)
                    for i, target in enumerate(eset.targets)
                    for targettree in target._get_trees()
                )

            return f

        optionlist = [genexp_func(clade) for clade in self.clades]

        # TODO is this duplicated code?
        for option in utils.cartesian_product(optionlist):
            tree = self.node_self()
            for clade, targettree, index in option:
                tree.clades[clade].add_to_edgeset(
                    targettree,
                    weight=self.clades[clade].weights[index],
                )
            yield tree

    def _newick_label(
        self,
        name_func: Callable[["HistoryDagNode"], str] = (lambda n: "unnamed"),
        features: Iterable[str] = None,
        feature_funcs: Mapping[str, Callable[["HistoryDagNode"], str]] = {},
    ) -> str:
        """Return an extended newick format node label.

        Args:
            name_func: A function which maps nodes to names
            features: A list of label fields to be recorded in extended newick format
            feature_funcs: A dictionary keyed by extended newick field names containing
                functions which map nodes to field values. These override fields named
                in `features`, if a key in `feature_funcs` is also contained in `features`.

        Returns:
            A string which can be used as a node name in a newick string.
            For example, `namefuncresult[&&NHX:feature1=val1:feature2=val2]`
        """
        if self.is_root():
            return self.label  # type: ignore
        else:
            if features is None:
                features = self.label._fields
            # Use dict to avoid duplicate fields
            nameval_dict = {
                name: val
                for name, val in self.label._asdict().items()
                if name in features
            }
            nameval_dict.update({name: f(self) for name, f in feature_funcs.items()})
            featurestr = ":".join(f"{name}={val}" for name, val in nameval_dict.items())
            return name_func(self) + (f"[&&NHX:{featurestr}]" if featurestr else "")


class UANode(HistoryDagNode):
    r"""A universal ancestor node, the root node of a HistoryDag"""

    def __init__(self, targetnodes: "EdgeSet"):
        self.label = UALabel()
        # an empty frozenset is not used as a key in any other node
        self.targetnodes = targetnodes
        self.clades = {frozenset(): targetnodes}
        self.parents = set()
        self.attr = dict()
        for child in self.children():
            child.parents.add(self)

    def node_self(self) -> "UANode":
        """Returns a UANode object with the same clades and label, but no
        descendant edges."""
        newnode = UANode(EdgeSet())
        newnode.attr = deepcopy(self.attr)
        return newnode

    def is_root(self):
        return True


class HistoryDag:
    r"""An object to represent a collection of internally labeled trees.
    A wrapper object to contain exposed HistoryDag methods and point to a HistoryDagNode root

    Args:
        dagroot: The root node of the history DAG
        attr: An attribute to contain data which will be preserved by copying (default and empty dict)
    """

    def __init__(self, dagroot: HistoryDagNode, attr: Any = {}):
        assert isinstance(dagroot, UANode)  # for typing
        self.attr = attr
        self.dagroot = dagroot
        self.current = 0

    def __eq__(self, other: object) -> bool:
        # Eventually this can be done by comparing bytestrings, but we need
        # some sorting to be done first, to ensure two dags that represent
        # identical trees return True. TODO
        raise NotImplementedError

    def __getitem__(self, key) -> "HistoryDag":
        r"""Returns the sub-history below the current history dag corresponding to the given index."""
        if key < 0:
            key = len(self) + key
        if isinstance(key, slice) or not type(key) == int:
            raise TypeError(f"History DAG indices must be integers, not {type(key)}")
        if not (key >= 0 and key < len(self)):
            raise IndexError
        self.count_trees()
        return HistoryDag(self.dagroot._get_subtree_by_subid(key))

    def __len__(self) -> int:
        self.count_trees()
        return self.dagroot._dp_data

    def __or__(self, other) -> "HistoryDag":
        newdag = self.copy()
        newdag.merge(other)
        return newdag

    def __ior__(self, other) -> "HistoryDag":
        self.merge(other)
        return self

    def __ror__(self, other) -> "HistoryDag":
        return other | self

    def __getstate__(self) -> Dict:
        r"""Converts HistoryDag to a bytestring-serializable dictionary.

        Since a HistoryDag is a recursive data structure, and contains label
        types defined in function scope, modifications must be made for pickling.

        Returns:
            A dictionary containing:
            * label_fields: The names of label fields.
            * label_list: labels used in nodes, without duplicates. Indices are
                mapped to nodes in node_list
            * node_list: node tuples containing
                (node label index in label_list, frozenset of frozensets of leaf label indices, node.attr).
            * edge_list: a tuple for each edge:
                    (origin node index, target node index, edge weight, edge probability)"""
        label_fields = list(self.dagroot.children())[0].label._fields
        label_list: List[Optional[Tuple]] = []
        node_list: List[Tuple] = []
        edge_list: List[Tuple] = []
        label_indices: Dict[Label, int] = {}
        node_indices = {id(node): idx for idx, node in enumerate(self.postorder())}

        def cladesets(node):
            clades = {
                frozenset({label_indices[label] for label in clade})
                for clade in node.clades
            }
            return frozenset(clades)

        for node in self.postorder():
            if node.label not in label_indices:
                label_indices[node.label] = len(label_list)
                label_list.append(None if node.is_root() else tuple(node.label))
                assert (
                    label_list[label_indices[node.label]] == node.label
                    or node.is_root()
                )
            node_list.append((label_indices[node.label], cladesets(node), node.attr))
            node_idx = len(node_list) - 1
            for eset in node.clades.values():
                for idx, target in enumerate(eset.targets):
                    edge_list.append(
                        (
                            node_idx,
                            node_indices[id(target)],
                            eset.weights[idx],
                            eset.probs[idx],
                        )
                    )
        serial_dict = {
            "label_fields": label_fields,
            "label_list": label_list,
            "node_list": node_list,
            "edge_list": edge_list,
            "attr": self.attr,
        }
        return serial_dict

    def __setstate__(self, serial_dict):
        """Rebuilds a HistoryDagNode using a serial_dict output by
        __getstate__"""
        label_list: List[Tuple] = serial_dict["label_list"]
        node_list: List[Tuple] = serial_dict["node_list"]
        edge_list: List[Tuple[int, int, float, float]] = serial_dict["edge_list"]
        label_fields: Tuple[str] = serial_dict["label_fields"]
        Label = NamedTuple("Label", [(label, any) for label in label_fields])  # type: ignore

        def unpack_labels(labelset):
            res = frozenset({Label(*label_list[idx]) for idx in labelset})
            return res

        node_postorder = [
            UANode(EdgeSet())
            if label_list[labelidx] is None
            else HistoryDagNode(
                (Label(*label_list[labelidx])),
                {unpack_labels(clade): EdgeSet() for clade in clades},
                attr,
            )
            for labelidx, clades, attr in node_list
        ]
        # Last node in list is root
        for origin_idx, target_idx, weight, prob in edge_list:
            node_postorder[origin_idx].add_edge(
                node_postorder[target_idx], weight=weight, prob=prob, prob_norm=False
            )
        self.dagroot = node_postorder[-1]
        self.attr = serial_dict["attr"]

    def serialize(self) -> bytes:
        return pickle.dumps(self.__getstate__())

    def get_trees(self) -> Generator["HistoryDag", None, None]:
        """Return a generator containing all trees in the history DAG.

        The order of these trees does not necessarily match the order of
        indexing. That is, ``dag.get_trees()`` and ``tree for tree in
        dag`` will result in different orderings. ``get_trees`` should
        be slightly faster, but possibly more memory intensive.
        """
        for cladetree in self.dagroot._get_trees():
            yield HistoryDag(cladetree)

    def sample(self) -> "HistoryDag":
        r"""Samples a clade tree from the history DAG.
        (A clade tree is a sub-history DAG containing the root and all
        leaf nodes). Returns a new HistoryDagNode object."""
        return HistoryDag(self.dagroot._sample())

    def is_clade_tree(self) -> bool:
        """Returns whether history DAG is a clade tree.

        That is, each node-clade pair has exactly one descendant edge.
        """
        for node in self.postorder():
            for clade, eset in node.clades.items():
                if len(eset.targets) != 1:
                    return False
        return True

    def copy(self) -> "HistoryDag":
        """Uses bytestring serialization, and is guaranteed to copy:

        * node labels
        * node attr attributes
        * edge weights
        * edge probabilities

        However, other object attributes will not be copied.
        """
        return pickle.loads(pickle.dumps(self))

    def merge(self, trees: Union["HistoryDag", Sequence["HistoryDag"]]):
        r"""Graph union this history DAG with all those in a list of history DAGs."""
        if isinstance(trees, HistoryDag):
            trees = [trees]

        selforder = self.postorder()
        nodedict = {n: n for n in selforder}

        for other in trees:
            if not self.dagroot == other.dagroot:
                raise ValueError(
                    f"The given HistoryDag must be a root node on identical taxa.\n{self.dagroot}\nvs\n{other.dagroot}"
                )
            otherorder = other.postorder()
            # hash and __eq__ are implemented for nodes, but we need to retrieve
            # the actual instance that's the same as a proposed node-to-add:
            for n in otherorder:
                if n in nodedict:
                    pnode = nodedict[n]
                else:
                    pnode = n.node_self()
                    nodedict[n] = pnode

                for _, edgeset in n.clades.items():
                    for child, weight, _ in edgeset:
                        pnode.add_edge(nodedict[child], weight=weight)

    def add_all_allowed_edges(
        self,
        new_from_root: bool = True,
        adjacent_labels: bool = True,
        preserve_parent_labels: bool = False,
    ) -> int:
        r"""Add all allowed edges to the DAG.

        Args:
            new_from_root: If False, no edges will be added that start at the DAG root.
                Useful when attempting to constrain root label.
            adjacent_labels: If False, no edges will be added between nodes with the same
                labels. Useful when attempting to maintain the history DAG in a 'collapsed'
                state.
            preserve_parent_labels: If True, ensures that for any edge added between a
                parent and child node, the parent node label was already among the original
                parent labels of the child node. This ensures that parsimony score is preserved.

        Returns:
            The number of edges added to the history DAG
        """
        n_added = 0
        clade_dict: Dict[FrozenSet[Label], List[HistoryDagNode]] = {
            node.under_clade(): [] for node in self.postorder()
        }
        if preserve_parent_labels is True:
            self.recompute_parents()
            uplabels = {
                node: {parent.label for parent in node.parents}
                for node in self.postorder()
            }

        # discard root node
        gen = self.preorder()
        next(gen)
        for node in gen:
            clade_dict[node.under_clade()].append(node)

        for node in self.postorder():
            if new_from_root is False and node.is_root():
                continue
            else:
                for clade in node.clades:
                    for target in clade_dict[clade]:
                        if adjacent_labels is False and target.label == node.label:
                            continue
                        elif (
                            preserve_parent_labels is True
                            and node.label not in uplabels[target]
                        ):
                            continue
                        else:
                            n_added += node.add_edge(target)
        return n_added

    @utils._cladetree_method
    def to_newick(
        self,
        name_func: Callable[[HistoryDagNode], str] = lambda n: "unnamed",
        features: Optional[List[str]] = None,
        feature_funcs: Mapping[str, Callable[[HistoryDagNode], str]] = {},
    ) -> str:
        r"""Converts clade tree to extended newick format.
        Supports arbitrary node names and a
        sequence feature. For use on a history DAG which is a clade tree.

        For extracting newick representations of trees in a general history DAG, see
        :meth:`HistoryDag.to_newicks`.

        Args:
            name_func: A map from nodes to newick node names
            features: A list of label field names to be included in extended newick data.
                If `None`, all label fields will be included. To include none of them,
                pass an empty list.
            feature_funcs: A dictionary keyed by extended newick field names, containing
                functions specifying how to populate that field for each node.

        Returns:
            A newick string. If `features` is an empty list, and feature_funcs is empty,
                then this will be a standard newick string. Otherwise, it will have ete3's
                extended newick format.
        """

        def newick(node):
            if node.is_leaf():
                return node._newick_label(
                    name_func, features=features, feature_funcs=feature_funcs
                )
            else:
                childnewicks = sorted([newick(node2) for node2 in node.children()])
                return (
                    "("
                    + ",".join(childnewicks)
                    + ")"
                    + node._newick_label(
                        name_func, features=features, feature_funcs=feature_funcs
                    )
                )

        return newick(next(self.dagroot.children())) + ";"

    @utils._cladetree_method
    def to_ete(
        self,
        name_func: Callable[[HistoryDagNode], str] = lambda n: "unnamed",
        features: Optional[List[str]] = None,
        feature_funcs: Mapping[str, Callable[[HistoryDagNode], str]] = {},
    ) -> ete3.TreeNode:
        """Convert a history DAG which is a clade tree to an ete tree.

        Args:
            name_func: A map from nodes to newick node names
            features: A list of label field names to be included in extended newick data.
                If `None`, all label fields will be included. To include none of them,
                pass an empty list.
            feature_funcs: A dictionary keyed by extended newick field names, containing
                functions specifying how to populate that field for each node.

        Returns:
            An ete3 Tree with the same topology as self, and node names and attributes
            as specified.
        """
        # First build a dictionary of ete3 nodes keyed by HDagNodes.
        if features is None:
            labelfeatures = list(
                list(self.dagroot.children())[0].label._asdict().keys()
            )
        else:
            labelfeatures = features

        def etenode(node: HistoryDagNode) -> ete3.TreeNode:
            newnode = ete3.TreeNode()
            newnode.name = name_func(node)
            for feature in labelfeatures:
                newnode.add_feature(feature, getattr(node.label, feature))
            for feature, func in feature_funcs.items():
                newnode.add_feature(feature, func(node))
            return newnode

        nodedict = {node: etenode(node) for node in self.preorder(skip_root=True)}

        for node in nodedict:
            for target in node.children():
                nodedict[node].add_child(child=nodedict[target])

        # Since self is cladetree, dagroot can have only one child
        return nodedict[list(self.dagroot.children())[0]]

    def to_graphviz(
        self,
        labelfunc: Optional[Callable[[HistoryDagNode], str]] = None,
        namedict: Mapping[Label, str] = {},
        show_partitions: bool = True,
    ) -> gv.Digraph:
        r"""Converts history DAG to graphviz (dot format) Digraph object.

        Args:
            labelfunc: A function to label nodes. If None, nodes will be labeled by
                their DAG node labels, or their label hash if label data is too large.
            namedict: A dictionary from node labels to label strings. Labelfunc will be
                used instead, if both are provided.
            show_partitions: Whether to include child clades in output.
        """

        def labeller(label):
            if label in namedict:
                return str(namedict[label])
            elif len(str(tuple(label))) < 11:
                return str(tuple(label))
            else:
                return str(hash(label))

        def taxa(clade):
            ls = [labeller(taxon) for taxon in clade]
            ls.sort()
            return ",".join(ls)

        if labelfunc is None:
            labelfunc = utils.ignore_uanode("UA_node")(lambda n: labeller(n.label))

        G = gv.Digraph("labeled partition DAG", node_attr={"shape": "record"})
        for node in self.postorder():
            if node.is_leaf() or show_partitions is False:
                G.node(str(id(node)), f"<label> {labelfunc(node)}")
            else:
                splits = "|".join(
                    [f"<{taxa(clade)}> {taxa(clade)}" for clade in node.clades]
                )
                G.node(str(id(node)), f"{{ <label> {labelfunc(node)} |{{{splits}}} }}")
            for clade in node.clades:
                for target, weight, prob in node.clades[clade]:
                    label = ""
                    if prob < 1.0:
                        label += f"p:{prob:.2f}"
                    if weight > 0.0:
                        label += f"w:{weight}"
                    G.edge(
                        f"{id(node)}:{taxa(clade) if show_partitions else 'label'}:s",
                        f"{id(target)}:n",
                        label=label,
                    )
        return G

    def internal_avg_parents(self) -> float:
        r"""Returns the average number of parents among internal nodes.
        A simple measure of similarity between the trees that the DAG expresses.
        However, keep in mind that two trees with the same topology but different labels
        would be considered entirely unalike by this measure."""
        nonleaf_parents = (len(n.parents) for n in self.postorder() if not n.is_leaf())
        n = 0
        cumsum = 0
        for sum in nonleaf_parents:
            n += 1
            cumsum += sum
        # Exclude root:
        return cumsum / float(n - 1)

    def make_uniform(self):
        """Adjust edge probabilities so that the DAG expresses a uniform
        distribution on expressed trees.

        The probability assigned to each edge below a clade is
        proportional to the number of subtrees possible below that edge.
        """
        self.count_trees()
        for node in self.postorder():
            for clade, eset in node.clades.items():
                for i, target in enumerate(eset.targets):
                    eset.probs[i] = target._dp_data

    def explode_nodes(
        self,
        expand_func: Callable[[Label], Iterable[Label]] = utils.sequence_resolutions,
        expandable_func: Callable[[Label], bool] = None,
    ) -> int:
        r"""Explode nodes according to a provided function.
        Adds copies of each node
        to the DAG with exploded labels, but with the same parents and children as the
        original node.

        Args:
            expand_func: A function that takes a node label, and returns an iterable
                containing 'exploded' or 'disambiguated' labels corresponding to the original.
                The wrapper :meth:`utils.explode_label` is provided to make such a function
                easy to write.
            expandable_func: A function that takes a node label, and returns whether the
                iterable returned by calling expand_func on that label would contain more
                than one item.

        Returns:
            The number of new nodes added to the history DAG.
        """

        if expandable_func is None:

            def is_ambiguous(label):
                # Check if expand_func(label) has at least two items, without
                # exhausting the (arbitrarily expensive) generator
                return len(list(zip([1, 2], expand_func(label)))) > 1

        else:
            is_ambiguous = expandable_func

        self.recompute_parents()
        nodedict = {node: node for node in self.postorder()}
        nodeorder = list(self.postorder())
        new_nodes = set()
        for node in nodeorder:
            if not node.is_root() and is_ambiguous(node.label):
                if node.is_leaf():
                    raise ValueError(
                        "Passed expand_func would explode a leaf node. "
                        "Leaf nodes may not be exploded."
                    )
                for resolution in expand_func(node.label):
                    newnodetemp = node.node_self()
                    newnodetemp.label = resolution
                    if newnodetemp in nodedict:
                        newnode = nodedict[newnodetemp]
                    else:
                        newnode = newnodetemp
                        nodedict[newnode] = newnode
                        new_nodes.add(newnode)
                    # Add all edges into and out of node to newnode
                    for target in node.children():
                        newnode.add_edge(target)
                    for parent in node.parents:
                        parent.add_edge(newnode)
                # Delete old node
                node.remove_node(nodedict=nodedict)
        return len(new_nodes)

    def summary(self):
        """Print nicely formatted summary about the history DAG."""
        print(f"Nodes:\t{sum(1 for _ in self.postorder())}")
        print(f"Trees:\t{self.count_trees()}")
        utils.hist(self.weight_counts_with_ambiguities())

    # ######## Abstract dp method and derivatives: ########

    def postorder_cladetree_accum(
        self,
        leaf_func: Callable[["HistoryDagNode"], Weight],
        edge_func: Callable[["HistoryDagNode", "HistoryDagNode"], Weight],
        accum_within_clade: Callable[[List[Weight]], Weight],
        accum_between_clade: Callable[[List[Weight]], Weight],
        accum_above_edge: Optional[Callable[[Weight, Weight], Weight]] = None,
    ) -> Weight:
        """A template method for leaf-to-root dynamic programming.

        Intermediate computations are stored in a `_dp_data` attribute on each node.
        Note that a `Weight` can be whatever you like, such as integers, Counters,
        strings, or dictionaries.

        Args:
            leaf_func: A function to assign weights to leaf nodes
            edge_func: A function to assign weights to edges. The parent node will
                always be the first argument.
            accum_within_clade: A function which accumulates a list of weights of subtrees
                below a single clade. That is, the weights are for alternative trees.
            accum_between_clade: A function which accumulates a list of weights of subtrees
                below different clades. That is, the weights are for different parts of the
                same tree.
            accum_above_edge: A function which adds the weight for a subtree to the weight
                of the edge above it. If `None`, this function will be inferred from
                `accum_between_clade`. The edge weight is the second argument.

        Returns:
            The resulting weight computed for the History DAG UA (root) node.
        """
        if accum_above_edge is None:

            def default_accum_above_edge(subtree_weight, edge_weight):
                return accum_between_clade([subtree_weight, edge_weight])

            accum_above_edge = default_accum_above_edge

        for node in self.postorder():
            if node.is_leaf():
                node._dp_data = leaf_func(node)
            else:
                node._dp_data = accum_between_clade(
                    [
                        accum_within_clade(
                            [
                                accum_above_edge(
                                    target._dp_data,
                                    edge_func(node, target),
                                )
                                for target in node.children(clade=clade)
                            ]
                        )
                        for clade in node.clades
                    ]
                )
        return self.dagroot._dp_data

    def optimal_weight_annotate(
        self,
        start_func: Callable[["HistoryDagNode"], Weight] = lambda n: 0,
        edge_weight_func: Callable[
            ["HistoryDagNode", "HistoryDagNode"], Weight
        ] = utils.wrapped_hamming_distance,
        accum_func: Callable[[List[Weight]], Weight] = sum,
        optimal_func: Callable[[List[Weight]], Weight] = min,
    ) -> Weight:
        r"""A template method for finding the optimal tree weight in the DAG.
        Dynamically annotates each node in the DAG with the optimal weight of a clade
        sub-tree beneath it, so that the DAG root node is annotated with the optimal
        weight of a clade tree in the DAG.

        Args:
            start_func: A function which assigns starting weights to leaves.
            edge_weight_func: A function which assigns weights to DAG edges based on the
                parent node and the child node, in that order.
            accum_func: A function which takes a list of weights of different parts of a
                tree, and returns a weight, like sum.
            optimal_func: A function which takes a list of weights and returns the optimal
                one, like min.

        Returns:
            The optimal weight of a tree under the DAG UA node.
        """
        return self.postorder_cladetree_accum(
            start_func,
            edge_weight_func,
            optimal_func,
            accum_func,
        )

    def weight_count(
        self,
        start_func: Callable[["HistoryDagNode"], Weight] = lambda n: 0,
        edge_weight_func: Callable[
            ["HistoryDagNode", "HistoryDagNode"], Weight
        ] = utils.wrapped_hamming_distance,
        accum_func: Callable[[List[Weight]], Weight] = sum,
    ):
        r"""A template method for counting weights of trees expressed in the history DAG.

        Weights must be hashable, but may otherwise be of arbitrary type.

        Args:
            start_func: A function which assigns a weight to each leaf node
            edge_func: A function which assigns a weight to pairs of labels, with the
                parent node label the first argument
            accum_func: A way to 'add' a list of weights together

        Returns:
            A Counter keyed by weights.
        """
        return self.postorder_cladetree_accum(
            lambda n: Counter([start_func(n)]),
            lambda n1, n2: Counter([edge_weight_func(n1, n2)]),
            counter_sum,
            lambda x: counter_prod(x, accum_func),
        )

    def hamming_parsimony_count(self):
        """Count the hamming parsimony scores of all trees in the history DAG.

        Returns a Counter with integer keys.
        """
        return self.weight_count(**utils.hamming_distance_countfuncs)

    def to_newicks(self, **kwargs):
        """Returns a list of extended newick strings formed with label fields.

        Arguments are passed to :meth:`utils.make_newickcountfuncs`.
        Arguments are the same as for
        :meth:`historydag.HistoryDag.to_newick`.
        """

        newicks = self.weight_count(**utils.make_newickcountfuncs(**kwargs)).elements()
        return [newick[1:-1] + ";" for newick in newicks]

    def count_topologies(self, collapse_leaves: bool = False) -> int:
        """Counts the number of unique topologies in the history DAG. This is
        achieved by counting the number of unique newick strings with only
        leaves labeled.

        :meth:`count_trees` gives the total number of unique trees in the DAG, taking
        into account internal node labels.

        Args:
            collapse_leaves: By default, topologies are counted as-is in the DAG. However,
                even if the DAG is collapsed by label, edges above leaf nodes will not be collapsed.
                if `collapse_leaves` is True, then the number of unique topologies with all
                leaf-adjacent edges collapsed will be counted. Assumes that the DAG is collapsed
                with :meth:`HistoryDag.convert_to_collapsed`.

        Returns:
            The number of topologies in the history DAG
        """
        kwargs = utils.make_newickcountfuncs(
            internal_labels=False, collapse_leaves=collapse_leaves
        )
        return len(self.weight_count(**kwargs))

    def count_trees(
        self,
        expand_func: Optional[Callable[[Label], List[Label]]] = None,
        expand_count_func: Callable[[Label], int] = lambda ls: 1,
    ):
        r"""Annotates each node in the DAG with the number of clade sub-trees underneath.

        Args:
            expand_func: A function which takes a label and returns a list of labels, for
                example disambiguations of an ambiguous sequence. If provided, this method
                will count at least the number of clade trees that would be in the DAG,
                if :meth:`explode_nodes` were called with the same `expand_func`.
            expand_count_func: A function which takes a label and returns an integer value
                corresponding to the number of 'disambiguations' of that label. If provided,
                `expand_func` will be used to find this value.

        Returns:
            The total number of unique complete trees below the root node. If `expand_func`
            or `expand_count_func` is provided, the complete trees being counted are not
            guaranteed to be unique.
        """
        if expand_func is not None:

            def expand_count_func(label):
                return len(list(expand_func(label)))

        return self.postorder_cladetree_accum(
            lambda n: 1,
            lambda parent, child: expand_count_func(child.label),
            sum,
            prod,
        )

    def weight_counts_with_ambiguities(
        self,
        start_func: Callable[["HistoryDagNode"], Weight] = lambda n: 0,
        edge_func: Callable[[Label, Label], Weight] = lambda l1, l2: (
            0 if isinstance(l1, UALabel) else utils.hamming_distance(l1.sequence, l2.sequence)  # type: ignore
        ),
        accum_func: Callable[[List[Weight]], Weight] = sum,
        expand_func: Callable[[Label], Iterable[Label]] = utils.sequence_resolutions,
    ):
        r"""Template method for counting tree weights in the DAG, with exploded labels.
        Like :meth:`weight_counts`, but creates dictionaries of Counter objects at each
        node, keyed by possible sequences at that node. Analogous to :meth:`count_trees`
        with `expand_func` provided.

        Weights must be hashable.

        Args:
            start_func: A function which assigns a weight to each leaf node
            edge_func: A function which assigns a weight to pairs of labels, with the
                parent node label the first argument. Must correctly handle the UA
                node label which is a UALabel instead of a namedtuple.
            accum_func: A way to 'add' a list of weights together
            expand_func: A function which takes a label and returns a list of labels, such
                as disambiguations of an ambiguous sequence.

        Returns:
            A Counter keyed by weights.
            The total number of trees will be greater than count_trees(), as these are
            possible disambiguations of trees. These disambiguations may not be unique,
            but if two are the same, they come from different subtrees of the DAG.
        """

        def wrapped_expand_func(label, is_root):
            if is_root:
                return [label]
            else:
                return expand_func(label)

        # The old direct implementation not using postorder_cladetree_accum was
        # more straightforward, and may be significantly faster.
        def leaf_func(node):
            return {
                label: Counter({start_func(node): 1})
                for label in expand_func(node.label)
            }

        def edge_weight_func(parent, child):
            # This will handle 'adding' child node counts to the edge, so we
            # have accum_above_edge just return this result.
            return {
                label: counter_sum(
                    [
                        counter_prod(
                            [target_wc, Counter({edge_func(label, childlabel): 1})],
                            accum_func,
                        )
                        for childlabel, target_wc in child._dp_data.items()
                    ]
                )
                for childlabel, target_wc in child._dp_data.items()
                for label in wrapped_expand_func(parent.label, parent.is_root())
            }

        def accum_within_clade(dictlist):
            keys = dictlist[0].keys()
            return {key: counter_sum([d[key] for d in dictlist]) for key in keys}

        def accum_between_clade(dictlist):
            keys = dictlist[0].keys()
            return {
                key: counter_prod([d[key] for d in dictlist], accum_func)
                for key in keys
            }

        return list(
            self.postorder_cladetree_accum(
                leaf_func,
                edge_weight_func,
                accum_within_clade,
                accum_between_clade,
                accum_above_edge=lambda n, e: e,
            ).values()
        )[0]

    # ######## End Abstract DP method derivatives ########

    def trim_optimal_weight(
        self,
        start_func: Callable[["HistoryDagNode"], Weight] = lambda n: 0,
        edge_weight_func: Callable[
            [HistoryDagNode, HistoryDagNode], Weight
        ] = utils.wrapped_hamming_distance,
        accum_func: Callable[[List[Weight]], Weight] = sum,
        optimal_func: Callable[[List[Weight]], Weight] = min,
        eq_func: Callable[[Weight, Weight], bool] = lambda w1, w2: w1 == w2,
    ) -> Weight:
        """Trims the DAG to only express trees with optimal weight. This is
        guaranteed to be possible when edge_weight_func depends only on the
        labels of an edge's parent and child node.

        Requires that weights are of a type that supports reliable equality
        testing. In particular, floats are not recommended. Instead, consider
        defining weights to be a precursor type, and define `optimal_func` to
        choose the one whose corresponding float is maximized/minimized.

        If floats must be used, a Numpy type may help.

        Args:
            start_func: A function which assigns starting weights to leaves.
            edge_weight_func: A function which assigns weights to DAG edges based on the
                parent node and the child node, in that order.
            accum_func: A function which takes a list of weights of different parts of a tree,
                and returns a weight, like sum.
            optimal_func: A function which takes a list of weights and returns the optimal
                one, like min.
            eq_func: A function which tests equality, taking a pair of weights and returning a bool.
        """
        opt_weight = self.optimal_weight_annotate(
            start_func=start_func,
            edge_weight_func=edge_weight_func,
            accum_func=accum_func,
            optimal_func=optimal_func,
        )
        # It may not be okay to use preorder here. May need reverse postorder
        # instead?
        for node in self.preorder():
            for clade, eset in node.clades.items():
                weightlist = [
                    (
                        accum_func([target._dp_data, edge_weight_func(node, target)]),
                        target,
                        index,
                    )
                    for index, target in enumerate(eset.targets)
                ]
                optimalweight = optimal_func([weight for weight, _, _ in weightlist])
                newtargets = []
                newweights = []
                for weight, target, index in weightlist:
                    if eq_func(weight, optimalweight):
                        newtargets.append(target)
                        newweights.append(eset.weights[index])
                eset.targets = newtargets
                eset.weights = newweights
                n = len(eset.targets)
                eset.probs = [1.0 / n] * n
        return opt_weight

    def get_topologies(self, collapse_leaves: bool = False) -> List[str]:
        """Return a list of pseudo-newick representations of topologies in the
        history DAG.

        The newicks returned are not well-formed, and are for use with
        :meth:`HistoryDag.trim_topology`. Otherwise, this method would be equivalent to
        :meth:`HistoryDag.to_newicks` with keyword arguments ``internal_labels=False`` and
        ``collapsed_leaves`` as desired.

        Args:
            collapse_leaves: Whether to collapse leaf-adjacent edges between nodes with
                matching labels

        Returns:
            A list of strings, each representing a topology present in the history DAG.
        """
        kwargs = utils.make_newickcountfuncs(
            internal_labels=False, collapse_leaves=collapse_leaves
        )
        return list(self.weight_count(**kwargs).keys())

    def trim_topology(self, topology: str, collapse_leaves: bool = False):
        """Trims the history DAG to express only trees matching the provided
        topology.

        Args:
            topology: A string like one output by :meth:`HistoryDag.get_topologies`
            collapse_leaves: must match the same argument provided to :meth:`HistoryDag.get_topologies`
                when creating the string passed as ``topology``.
        """

        def min_func(newicks: List[str]) -> str:
            # Each newick in presented to min_func will be well-formed, since
            # it will consist of a subtree newick added to a parent edge's
            # newick.
            for newick in newicks:
                if newick in topology:
                    return newick
            if newicks:
                return "(;)"
            else:
                raise ValueError("min_func() arg is an empty sequence")

        self.trim_optimal_weight(
            **utils.make_newickcountfuncs(
                internal_labels=False, collapse_leaves=collapse_leaves
            ),
            optimal_func=min_func,
        )

    def recompute_parents(self):
        """Repopulate ``HistoryDagNode.parent`` attributes."""
        for node in self.postorder():
            node.parents = set()
        for node in self.postorder():
            for child in node.children():
                child.parents.add(node)

    def convert_to_collapsed(self):
        r"""Rebuilds the DAG so that no edge connects two nodes with the same label,
        unless one is a leaf node.

        The resulting DAG should express at least the collapsed clade trees present
        in the original.
        """

        self.recompute_parents()
        nodes = list(self.postorder())
        nodedict = {node: node for node in nodes}
        edgequeue = [
            [parent, target] for parent in nodes for target in parent.children()
        ]

        while edgequeue:
            parent, child = edgequeue.pop()
            clade = child.under_clade()
            if (
                parent.label == child.label
                and parent in nodedict
                and child in nodedict
                and not child.is_leaf()
            ):
                parent_clade_edges = len(parent.clades[clade].targets)
                new_parent_clades = (
                    frozenset(parent.clades.keys()) - {clade}
                ) | frozenset(child.clades.keys())
                newparenttemp = empty_node(
                    parent.label, new_parent_clades, deepcopy(parent.attr)
                )
                if newparenttemp in nodedict:
                    newparent = nodedict[newparenttemp]
                else:
                    newparent = newparenttemp
                    nodedict[newparent] = newparent
                # Add parents of parent to newparent
                for grandparent in parent.parents:
                    grandparent.add_edge(newparent)  # check parents logic
                    edgequeue.append([grandparent, newparent])
                # Add children of other clades to newparent
                for otherclade in parent.clades:
                    if otherclade != clade:
                        for othertarget in parent.clades[otherclade].targets:
                            newparent.add_edge(othertarget)
                            edgequeue.append([newparent, othertarget])
                # Add children of old child to newparent
                for grandchild in child.children():
                    newparent.add_edge(grandchild)
                    edgequeue.append([newparent, grandchild])
                # Remove the edge we were fixing from old parent
                parent.remove_edge_by_clade_and_id(child, clade)
                # Clean up the DAG:
                # Delete old parent if it is no longer a valid node
                if parent_clade_edges == 1:
                    # Remove old parent as child of all of its parents
                    # no need for recursion here, all of its parents had
                    # edges added to new parent from the same clade.
                    upclade = parent.under_clade()
                    for grandparent in parent.parents:
                        grandparent.remove_edge_by_clade_and_id(parent, upclade)
                    for child2 in parent.children():
                        child2.parents.remove(parent)
                        if not child2.parents:
                            child2.remove_node(nodedict=nodedict)
                    nodedict.pop(parent)

                # Remove child, if child no longer has parents
                if parent in child.parents:
                    child.parents.remove(parent)
                if not child.parents:
                    # This recursively removes children of child too, if necessary
                    child.remove_node(nodedict=nodedict)
        self.recompute_parents()

    # ######## DAG Traversal Methods ########

    def postorder(
        self, include_root: bool = True
    ) -> Generator[HistoryDagNode, None, None]:
        """Recursive postorder traversal of the history DAG.

        Returns:
            Generator on nodes
        """
        visited = set()

        def traverse(node: HistoryDagNode):
            visited.add(id(node))
            if not node.is_leaf():
                for child in node.children():
                    if not id(child) in visited:
                        yield from traverse(child)
            yield node

        yield from traverse(self.dagroot)

    def preorder(self, skip_root=False) -> Generator[HistoryDagNode, None, None]:
        """Recursive postorder traversal of the history DAG.

        Careful! This is not guaranteed to visit a parent node before any of its children.
        for that, need reverse postorder traversal.

        Returns:
            Generator on nodes
        """
        visited = set()

        def traverse(node: HistoryDagNode):
            visited.add(id(node))
            yield node
            if not node.is_leaf():
                for child in node.children():
                    if not id(child) in visited:
                        yield from traverse(child)

        gen = traverse(self.dagroot)
        if skip_root:
            next(gen)
        yield from gen


class EdgeSet:
    r"""
    A container class for edge target nodes, and associated probabilities and weights.
    Goal: associate targets (edges) with arbitrary parameters, but support
    set-like operations like lookup and enforce that elements are unique."""

    def __init__(
        self,
        *args,
        weights: Optional[List[float]] = None,
        probs: Optional[List[float]] = None,
    ):
        r"""Takes no arguments, or an ordered iterable containing target nodes"""
        if len(args) > 1:
            raise TypeError(f"Expected at most one argument, got {len(args)}")
        elif args:
            self.targets = list(args[0])
            n = len(self.targets)
            if weights is not None:
                self.weights = weights
            else:
                self.weights = [0] * n

            if probs is not None:
                self.probs = probs
            else:
                self.probs = [float(1) / n] * n
        else:
            self.targets = []
            self.weights = []
            self.probs = []
            self._targetset = set()

        self._targetset = set(self.targets)
        if not len(self._targetset) == len(self.targets):
            raise TypeError("First argument may not contain duplicate target nodes")
        # Should probably also check to see that all passed lists have same length

    def __iter__(self):
        return (
            (self.targets[i], self.weights[i], self.probs[i])
            for i in range(len(self.targets))
        )

    def shallowcopy(self) -> "EdgeSet":
        """Return an identical EdgeSet object, which points to the same target
        nodes."""
        return EdgeSet(
            [node for node in self.targets],
            weights=self.weights.copy(),
            probs=self.probs.copy(),
        )

    def remove_from_edgeset_byid(self, target_node):
        idlist = [id(target) for target in self.targets]
        if id(target_node) in idlist:
            idx_to_remove = idlist.index(id(target_node))
            self.targets.pop(idx_to_remove)
            self.probs.pop(idx_to_remove)
            self.weights.pop(idx_to_remove)
            self._targetset = set(self.targets)

    def sample(self) -> Tuple[HistoryDagNode, float]:
        """Returns a randomly sampled child edge, and its corresponding
        weight."""
        index = random.choices(list(range(len(self.targets))), weights=self.probs, k=1)[
            0
        ]
        return (self.targets[index], self.weights[index])

    def add_to_edgeset(self, target, weight=0, prob=None, prob_norm=True) -> bool:
        """Add a target node to the EdgeSet.

        currently does nothing if edge is already present. Also does nothing
        if the target node has one child clade, and parent node is not the DAG root.

        Args:
            target: target node
            weight: edge weight
            prob: edge probability. If not provided, edge probability will be
                1 / n where n is the number of edges in the edgeset.
            prob_norm: if True, probability vector will be normalized.

        Returns:
            Whether an edge was added
        """
        if target.is_root():
            raise ValueError(
                "Edges that target UA nodes are not allowed. "
                f"Target node has label {target.label} and therefore "
                "is assumed to be the DAG UA root node."
            )
        elif target in self._targetset:
            return False
        else:
            self._targetset.add(target)
            self.targets.append(target)
            self.weights.append(weight)

            if prob is None:
                prob = 1.0 / len(self.targets)
            if prob_norm:
                self.probs = list(
                    map(lambda x: x * (1 - prob) / sum(self.probs), self.probs)
                )
            self.probs.append(prob)
            return True


# ######## DAG Creation Functions ########


def empty_node(
    label: Label, clades: Iterable[FrozenSet[Label]], attr: Any = None
) -> HistoryDagNode:
    """Return a HistoryDagNode with the given label and clades, with no
    children."""
    return HistoryDagNode(label, {clade: EdgeSet() for clade in clades}, attr)


def from_tree(
    tree: ete3.TreeNode,
    label_features: List[str],
    label_functions: Mapping[str, Callable[[ete3.TreeNode], Any]] = {},
    attr_func: Callable[[ete3.TreeNode], Any] = lambda n: None,
) -> HistoryDag:
    """Build a full tree from an ete3 TreeNode.

    Args:
        tree: ete3 tree to be converted to HistoryDag clade tree
        label_features: node attribute names to be used to distinguish nodes. Field names
            provided in `label_functions` will take precedence.
        label_functions: dictionary keyed by additional label field names, containing
            functions mapping tree nodes to intended label field value.
        attr_func: function to populate HistoryDag node `attr` attribute,
            which is not used to distinguish nodes, and may be overwritten
            by `attr` of another node with the same label and child clades.

    Returns:
        HistoryDag object, which has the same topology as the input tree, with the required
        UA node added as a new root.
    """
    # see https://stackoverflow.com/questions/50298582/why-does-python-asyncio-loop-call-soon-overwrite-data
    # or https://stackoverflow.com/questions/25670516/strange-overwriting-occurring-when-using-lambda-functions-as-dict-values
    # for why we can't just use lambda funcs defined in dict comprehension.
    def getnamefunc(name):
        def getter(node):
            return getattr(node, name)

        return getter

    feature_maps = {name: getnamefunc(name) for name in label_features}
    feature_maps.update(label_functions)
    Label = NamedTuple("Label", [(label, Any) for label in feature_maps.keys()])  # type: ignore

    def node_label(n: ete3.TreeNode):
        # This should not fail silently! Only DAG UA node is allowed to have
        # default (None) label values.
        return Label(**{name: f(n) for name, f in feature_maps.items()})

    def leaf_names(r: ete3.TreeNode):
        return frozenset((node_label(node) for node in r.get_leaves()))

    def _unrooted_from_tree(tree):
        dag = HistoryDagNode(
            node_label(tree),
            {
                leaf_names(child): EdgeSet(
                    [_unrooted_from_tree(child)], weights=[child.dist]
                )
                for child in tree.children
            },
            attr_func(tree),
        )
        return dag

    # Check for unique leaf labels:
    if len(list(tree.get_leaves())) != len(leaf_names(tree)):
        raise ValueError(
            "This tree's leaves are not labeled uniquely. Check your tree, "
            "or modify the label fields so that leaves are unique.\n"
        )

    # Checking for unifurcation is handled in HistoryDagNode.__init__.

    dag = _unrooted_from_tree(tree)
    dagroot = UANode(EdgeSet([dag], weights=[tree.dist]))
    dagroot.add_edge(dag, weight=0)
    return HistoryDag(dagroot)


def from_newick(
    tree: str,
    label_features: List[str],
    label_functions: Mapping[str, Callable[[ete3.TreeNode], Any]] = {},
    newick_format=8,
    attr_func: Callable[[ete3.TreeNode], Any] = lambda n: None,
) -> HistoryDag:
    """Make a history DAG using a newick string. Internally, utilizes newick
    parsing features provided by ete3, then calls :meth:`from_tree` on the
    resulting ete3.Tree object.

    Args:
        tree: newick string representation of a tree. May contain extended node data
            in 'extended newick format' used by ete3.
        label_features: (passed to :meth:`from_tree`) list of features to be used as label
            fields in resulting history DAG.  'name' refers to the node name string in the
            standard newick format. See ete3 docs for more details.
        newick_format: ete3 format number of passed newick string. See ete3 docs for details.
        label_functions: (passed to :meth:`from_tree`)
        attr_func: (passed to :meth:`from_tree`)

    Returns:
        HistoryDag object, which has the same topology as the input newick tree, with the
        required UA node added as a new root.
    """
    etetree = ete3.Tree(tree, format=newick_format)
    # from_tree checks that leaves are labeled uniquely. If this function is
    # ever rewritten to avoid ete newick parsing, we'd need to do that here.
    return from_tree(
        etetree, label_features, label_functions=label_functions, attr_func=attr_func
    )


def history_dag_from_newicks(
    newicklist: List[str],
    label_features: List[str],
    label_functions: Mapping[str, Callable[[ete3.TreeNode], Any]] = {},
    attr_func: Callable[[ete3.TreeNode], Any] = lambda n: None,
    newick_format=1,
) -> HistoryDag:
    """Build a history DAG from a list of newick strings.

    See :meth:`from_newick` for argument details.
    """
    return history_dag_from_clade_trees(
        [
            from_newick(
                tree,
                label_features,
                label_functions=label_functions,
                attr_func=attr_func,
                newick_format=newick_format,
            )
            for tree in newicklist
        ]
    )


def history_dag_from_etes(
    treelist: List[ete3.TreeNode],
    label_features: List[str],
    label_functions: Mapping[str, Callable[[ete3.TreeNode], Any]] = {},
    attr_func: Callable[[ete3.TreeNode], Any] = lambda n: None,
) -> HistoryDag:
    """Build a history DAG from a list of ete3 Trees.

    See :meth:`from_tree` for argument details.
    """
    return history_dag_from_clade_trees(
        [
            from_tree(
                tree,
                label_features,
                label_functions=label_functions,
                attr_func=attr_func,
            )
            for tree in treelist
        ]
    )


def history_dag_from_clade_trees(treelist: List[HistoryDag]) -> HistoryDag:
    """Build a history DAG from a list of history DAGs which are clade
    trees."""
    # merge checks that all clade trees have the same leaf label set.
    dag = treelist[0].copy()
    dag.merge(treelist[1:])
    return dag
