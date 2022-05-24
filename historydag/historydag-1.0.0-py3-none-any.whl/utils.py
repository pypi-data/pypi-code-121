"""Utility functions and classes for working with HistoryDag objects."""

import ete3
from Bio.Data.IUPACData import ambiguous_dna_values
from collections import Counter
from functools import wraps
from collections import UserDict
from decimal import Decimal
from typing import (
    List,
    Any,
    TypeVar,
    Callable,
    Union,
    Iterable,
    Generator,
    Tuple,
    NamedTuple,
    Optional,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from historydag.dag import HistoryDagNode

Weight = Any
Label = Union[NamedTuple, "UALabel"]
F = TypeVar("F", bound=Callable[..., Any])


class UALabel(str):
    _fields: Tuple = tuple()

    def __new__(cls):
        return super(UALabel, cls).__new__(cls, "UA_Node")

    def __eq__(self, other):
        return isinstance(other, UALabel)

    def __hash__(self):
        return hash("UA_Node")

    def __iter__(self):
        raise RuntimeError("Attempted to iterate from dag root UALabel")

    def _asdict(self):
        raise RuntimeError("Attempted to iterate from dag root UALabel")


bases = "AGCT-"
ambiguous_dna_values.update({"?": bases, "-": "-"})


# ######## Decorators ########
def access_nodefield_default(fieldname: str, default: Any) -> Any:
    """A decorator for accessing label fields on a HistoryDagNode. Converts a
    function taking some label field's values as positional arguments, to a
    function taking HistoryDagNodes as positional arguments.

    Args:
        fieldname: The name of the label field whose value the function takes as arguments
        default: A value that should be returned if one of the arguments is the DAG UA node.

    For example, instead of
    `lambda n1, n2: default if n1.is_root() or n2.is_root() else func(n1.label.fieldname, n2.label.fieldname)`,
    this wrapper allows one to write `access_nodefield_default(fieldname, default)(func)`.
    """

    def decorator(func):
        @ignore_uanode(default)
        @access_field("label")
        @access_field(fieldname)
        @wraps(func)
        def wrapper(*args: Label, **kwargs: Any) -> Weight:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def access_field(fieldname: str) -> Callable[[F], F]:
    """A decorator for conveniently accessing a field in a label.

    To be used instead of something like `lambda l1, l2:
    func(l1.fieldname, l2.fieldname)`. Instead just write
    `access_field(fieldname)(func)`. Supports arbitrarily many
    positional arguments, which are all expected to be labels
    (namedtuples) with field `fieldname`.
    """

    def decorator(func: F):
        @wraps(func)
        def wrapper(*args: Label, **kwargs: Any) -> Any:
            newargs = [getattr(label, fieldname) for label in args]
            return func(*newargs, **kwargs)

        return wrapper

    return decorator


def ignore_uanode(default: Any) -> Callable[[F], F]:
    """A decorator to return a default value if any argument is a UANode.

    For instance, to allow distance between two nodes to be zero if one
    is UANode
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args: "HistoryDagNode", **kwargs: Any):
            for node in args:
                if node.is_root():
                    return default
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def explode_label(labelfield: str):
    """A decorator to make it easier to expand a Label by a certain field.

    Args:
        labelfield: the name of the field whose contents the wrapped function is expected to
            explode

    Returns:
        A decorator which converts a function which explodes a field value, into a function
        which explodes the whole label at that field.
    """

    def decorator(
        func: Callable[[Any], Iterable[Any]]
    ) -> Callable[[Label], Iterable[Label]]:
        @wraps(func)
        def wrapfunc(label, *args, **kwargs):
            Label = type(label)
            d = label._asdict()
            for newval in func(d[labelfield], *args, **kwargs):
                d[labelfield] = newval
                yield Label(**d)

        return wrapfunc

    return decorator


# ######## Distances and comparisons... ########


def hamming_distance(s1: str, s2: str) -> int:
    """The sitewise sum of base differences between s1 and s2."""
    if len(s1) != len(s2):
        raise ValueError("Sequences must have the same length!")
    return sum(x != y for x, y in zip(s1, s2))


@access_nodefield_default("sequence", 0)
def wrapped_hamming_distance(s1, s2) -> int:
    """The sitewise sum of base differences between sequence field contents of
    two nodes.

    Takes two HistoryDagNodes as arguments.

    If l1 or l2 is a UANode, returns 0.
    """
    return hamming_distance(s1, s2)


def is_ambiguous(sequence: str) -> bool:
    """Returns whether the provided sequence contains IUPAC nucleotide
    ambiguity codes."""
    return any(code not in bases for code in sequence)


def cartesian_product(
    optionlist: List[Callable[[], Iterable]], accum=tuple()
) -> Generator[Tuple, None, None]:
    """The cartesian product of iterables in a list.

    Takes a list of functions which each return a fresh generator on
    options at that site, and returns a generator yielding tuples, which
    are elements of the cartesian product of the passed generators'
    contents.
    """
    if optionlist:
        for term in optionlist[0]():
            yield from cartesian_product(optionlist[1:], accum=(accum + (term,)))
    else:
        yield accum


@explode_label("sequence")
def sequence_resolutions(sequence: str) -> Generator[str, None, None]:
    """Iterates through possible disambiguations of sequence, recursively.

    Recursion-depth-limited by number of ambiguity codes in sequence,
    not sequence length.
    """

    def _sequence_resolutions(sequence, _accum=""):
        if sequence:
            for index, base in enumerate(sequence):
                if base in bases:
                    _accum += base
                else:
                    for newbase in ambiguous_dna_values[base]:
                        yield from _sequence_resolutions(
                            sequence[index + 1 :], _accum=(_accum + newbase)
                        )
                    return
        yield _accum

    return _sequence_resolutions(sequence)


@access_field("sequence")
def sequence_resolutions_count(sequence: str) -> int:
    """Count the number of possible sequence resolutions Equivalent to the
    length of the list returned by :meth:`sequence_resolutions`."""
    base_options = [
        len(ambiguous_dna_values[base])
        for base in sequence
        if base in ambiguous_dna_values
    ]
    return prod(base_options)


def hist(c: Counter, samples: int = 1):
    """Pretty prints a counter Normalizing counts using the number of samples,
    passed as the argument `samples`."""
    ls = list(c.items())
    ls.sort()
    print("Weight\t| Frequency\n------------------")
    for weight, freq in ls:
        print(f"{weight}  \t| {freq if samples==1 else freq/samples}")


def is_collapsed(tree: ete3.TreeNode) -> bool:
    """Return whether the provided tree is collapsed.

    Collapsed means that any edge whose target is not a leaf node
    connects nodes with different sequences.
    """
    return not any(
        node.sequence == node.up.sequence and not node.is_leaf()
        for node in tree.iter_descendants()
    )


def collapse_adjacent_sequences(tree: ete3.TreeNode) -> ete3.TreeNode:
    """Collapse nonleaf nodes that have the same sequence."""
    # Need to keep doing this until the tree fully collapsed. See gctree for this!
    tree = tree.copy()
    to_delete = []
    for node in tree.get_descendants():
        # This must stay invariably hamming distance, since it's measuring equality of strings
        if (
            not node.is_leaf()
            and hamming_distance(node.up.sequence, node.sequence) == 0
        ):
            to_delete.append(node)
    for node in to_delete:
        node.delete()
    return tree


class AddFuncDict(UserDict):
    """Container for function keyword arguments to
    :meth:`historydag.HistoryDag.weight_count`. This is primarily useful
    because it allows instances to be added. Passing the result to
    `weight_count` as keyword arguments counts the weights jointly. A
    :class:`historydag.utils.AddFuncDict` which may be passed as keyword
    arguments to :meth:`historydag.HistoryDag.weight_count`,
    :meth:`historydag.HistoryDag.trim_optimal_weight`, or
    :meth:`historydag.HistoryDag.optimal_weight_annotate` methods to trim or
    annotate a :meth:`historydag.HistoryDag` according to the weight that the
    contained functions implement.

    For example, `dag.weight_count(**(utils.hamming_distance_countfuncs + make_newickcountfuncs()))`
    would return a Counter object in which the weights are tuples containing hamming parsimony and newickstrings.

    Args:
        initialdata: A dictionary containing functions keyed by "start_func", "edge_weight_func", and
            "accum_func". "start_func" specifies weight assigned to leaf HistoryDagNodes.
            "edge_weight_func" specifies weight assigned to an edge between two HistoryDagNodes, with the
            first argument the parent node, and the second argument the child node.
            "accum_func" specifies how to 'add' a list of weights. See :meth:`historydag.HistoryDag.weight_count`
            for more details.
        name: A string containing a name for the weight to be counted. If a tuple of weights will be returned,
            use ``names`` instead.
        names: A tuple of strings containing names for the weights to be counted, if a tuple of weights will
            be returned by passed functions. If only a single weight will be returned, use ``name`` instead.
    """

    requiredkeys = {"start_func", "edge_weight_func", "accum_func"}

    def __init__(self, initialdata, name: str = None, names: Tuple[str] = None):
        self.name: Optional[str]
        self.names: Tuple[str]
        if name is not None and names is not None:
            raise ValueError(
                "Pass a value to either keyword argument 'name' or 'names'."
            )
        elif name is None and names is None:
            self.name = "unknown weight"
            self.names = (self.name,)
        elif name is not None:
            self.name = name
            self.names = (self.name,)
        elif names is not None:
            self.names = names
            self.name = None
        if not set(initialdata.keys()) == self.requiredkeys:
            raise ValueError(
                "Must provide functions named " + ", ".join(self.requiredkeys)
            )
        super().__init__(initialdata)

    def __add__(self, other) -> "AddFuncDict":
        fdict1 = self._convert_to_tupleargs()
        fdict2 = other._convert_to_tupleargs()
        n = len(fdict1.names)

        def newaccumfunc(weightlist):
            return fdict1["accum_func"](
                [weight[0:n] for weight in weightlist]
            ) + fdict2["accum_func"]([weight[n:] for weight in weightlist])

        def addfuncs(func1, func2):
            def newfunc(*args):
                return func1(*args) + func2(*args)

            return newfunc

        return AddFuncDict(
            {
                "start_func": addfuncs(fdict1["start_func"], fdict2["start_func"]),
                "edge_weight_func": addfuncs(
                    fdict1["edge_weight_func"], fdict2["edge_weight_func"]
                ),
                "accum_func": newaccumfunc,
            },
            names=fdict1.names + fdict2.names,
        )

    def _convert_to_tupleargs(self):
        if self.name is not None:

            def node_to_weight_decorator(func):
                @wraps(func)
                def wrapper(*args):
                    return (func(*args),)

                return wrapper

            def list_of_weights_to_weight_decorator(func):
                @wraps(func)
                def wrapper(weighttuplelist: List[Weight]):
                    return (func([wt[0] for wt in weighttuplelist]),)

                return wrapper

            return AddFuncDict(
                {
                    "start_func": node_to_weight_decorator(self["start_func"]),
                    "edge_weight_func": node_to_weight_decorator(
                        self["edge_weight_func"]
                    ),
                    "accum_func": list_of_weights_to_weight_decorator(
                        self["accum_func"]
                    ),
                },
                names=(self.name,),
            )
        else:
            return self


hamming_distance_countfuncs = AddFuncDict(
    {
        "start_func": lambda n: 0,
        "edge_weight_func": wrapped_hamming_distance,
        "accum_func": sum,
    },
    name="HammingParsimony",
)
"""Provides functions to count hamming distance parsimony.
For use with :meth:`historydag.HistoryDag.weight_count`."""


def make_newickcountfuncs(
    name_func=lambda n: "unnamed",
    features=None,
    feature_funcs={},
    internal_labels=True,
    collapse_leaves=False,
):
    """Provides functions to count newick strings. For use with
    :meth:`historydag.HistoryDag.weight_count`.

    Arguments are the same as for
    :meth:`historydag.HistoryDag.to_newick`.
    """

    def _newicksum(newicks):
        # Filter out collapsed/deleted edges
        snewicks = sorted(newicks)
        if len(snewicks) == 2 and ";" in [newick[-1] for newick in snewicks if newick]:
            # Then we are adding an edge above a complete tree
            return "".join(
                sorted(snewicks, key=lambda n: ";" == n[-1] if n else False)
            )[:-1]
        else:
            # Then we're just accumulating options between clades
            return "(" + ",".join(snewicks) + ")"

    def _newickedgeweight(n1, n2):
        if collapse_leaves and n2.is_leaf() and n1.label == n2.label:
            return "COLLAPSED_LEAF;"
        elif (
            internal_labels
            or n2.is_leaf()
            or (collapse_leaves and frozenset({n2.label}) in n2.clades)
        ):
            return (
                n2._newick_label(
                    name_func=name_func, features=features, feature_funcs=feature_funcs
                )
                + ";"
            )
        else:
            return ";"

    return AddFuncDict(
        {
            "start_func": lambda n: "",
            "edge_weight_func": _newickedgeweight,
            "accum_func": _newicksum,
        },
        name="NewickString",
    )


def _cladetree_method(method):
    """HistoryDagNode method decorator to ensure that the method is only run on
    history DAGs which are clade trees."""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.is_clade_tree():
            raise ValueError(
                "to_newick requires the history DAG to be a clade tree. "
                "To extract newicks from a general DAG, see to_newicks"
            )
        else:
            return method(self, *args, **kwargs)

    return wrapper


def prod(ls: list):
    """Return product of elements of the input list.

    if passed list is empty, returns 1.
    """
    n = len(ls)
    if n > 0:
        accum = ls[0]
        if n > 1:
            for item in ls[1:]:
                accum *= item
    else:
        accum = 1
    return accum


# Unfortunately these can't be made with a class factory (just a bit too meta for Python)
# short of doing something awful like https://hg.python.org/cpython/file/b14308524cff/Lib/collections/__init__.py#l232
def _remstate(kwargs):
    if "state" not in kwargs:
        kwargs["state"] = None
    intkwargs = kwargs.copy()
    intkwargs.pop("state")
    return intkwargs


class IntState(int):
    """A subclass of int, with arbitrary, mutable state.

    State is provided to the constructor as the keyword argument
    ``state``. All other arguments will be passed to ``int``
    constructor. Instances should be functionally indistinguishable from
    ``int``.
    """

    def __new__(cls, *args, **kwargs):
        intkwargs = _remstate(kwargs)
        return super(IntState, cls).__new__(cls, *args, **intkwargs)

    def __init__(self, *args, **kwargs):
        self.state = kwargs["state"]

    def __copy__(self):
        return IntState(int(self), state=self.state)

    def __getstate__(self):
        return {"val": int(self), "state": self.state}

    def __setstate__(self, statedict):
        self.state = statedict["state"]


class FloatState(float):
    """A subclass of float, with arbitrary, mutable state.

    State is provided to the constructor as the keyword argument
    ``state``. All other arguments will be passed to ``float``
    constructor. Instances should be functionally indistinguishable from
    ``float``.
    """

    def __new__(cls, *args, **kwargs):
        intkwargs = _remstate(kwargs)
        return super(FloatState, cls).__new__(cls, *args, **intkwargs)

    def __init__(self, *args, **kwargs):
        self.state = kwargs["state"]

    def __copy__(self):
        return FloatState(float(self), state=self.state)

    def __getstate__(self):
        return {"val": float(self), "state": self.state}

    def __setstate__(self, statedict):
        self.state = statedict["state"]


class DecimalState(Decimal):
    """A subclass of ``decimal.Decimal``, with arbitrary, mutable state.

    State is provided to the constructor as the keyword argument
    ``state``. All other arguments will be passed to ``Decimal``
    constructor. Instances should be functionally indistinguishable from
    ``Decimal``.
    """

    def __new__(cls, *args, **kwargs):
        intkwargs = _remstate(kwargs)
        return super(DecimalState, cls).__new__(cls, *args, **intkwargs)

    def __init__(self, *args, **kwargs):
        self.state = kwargs["state"]

    def __copy__(self):
        return DecimalState(Decimal(self), state=self.state)

    def __getstate__(self):
        return {"val": Decimal(self), "state": self.state}

    def __setstate__(self, statedict):
        self.state = statedict["state"]


class StrState(str):
    """A subclass of string, with arbitrary, mutable state.

    State is provided to the constructor as the keyword argument
    ``state``. All other arguments will be passed to ``str``
    constructor. Instances should be functionally indistinguishable from
    ``str``.
    """

    def __new__(cls, *args, **kwargs):
        intkwargs = _remstate(kwargs)
        return super(StrState, cls).__new__(cls, *args, **intkwargs)

    def __init__(self, *args, **kwargs):
        self.state = kwargs["state"]

    def __copy__(self):
        return StrState(str(self), state=self.state)

    def __getstate__(self):
        return {"val": str(self), "state": self.state}

    def __setstate__(self, statedict):
        self.state = statedict["state"]
