"""The memory-based graphmaster."""
from typing import Optional, Any, Callable, List, Tuple, TypeVar, Union, Set
import dill
from pyaiml21.ast import Node, Category
from pyaiml21.botconfig import BotConfig
from pyaiml21.parser import Logger
from .node import GMNode
from .stars import StarBindings
from .pattern import Pattern


KEEP_FIRST_POLICY = "keep_first"
KEEP_LAST_POLICY = "keep_last"


T = TypeVar("T")
StoredObj = Any
PolicyFn = Callable[[StoredObj, StoredObj], StoredObj]
"""Function called to handle two matching patterns to merge their objects"""


# predefined merge policies
def _load_first_policy(x, _):
    return x


def _load_last_policy(_, y):
    return y


def _resolve_policy(policy: Union[str, PolicyFn]) -> PolicyFn:
    if not isinstance(policy, str):
        return policy
    if policy == KEEP_FIRST_POLICY:
        return _load_first_policy
    elif policy == KEEP_LAST_POLICY:
        return _load_last_policy
    else:
        raise TypeError(f"unknown type of merge policy: '{policy}', "
                        f"consider using KEEP_FIRST_POLICY or "
                        f"KEEP_LAST_POLICY, or implement a custom policy")


def _insort(e: T, seq: List[T], key: Callable[[T], Any]):
    """
    Insert `e` into sorted sequence `seq`.

    Add element `e` to list `seq` so that `seq` is sorted ascending with
    respect to the `key`. The `seq` is expected to be already sorted.
    """
    seq.append(e)
    for i in reversed(range(1, len(seq))):
        if key(seq[i]) <= key(seq[i - 1]):
            seq[i], seq[i - 1] = seq[i - 1], seq[i]
        else:
            break


###############################################################################
#                          G R A P H M A S T E R
###############################################################################


class GraphMaster:
    """
    GraphMaster is a pattern matching data structure.

    It stores AIML categories in the tree-like structure
    (directed word graph/tree) and uses backtracking to find the first match.

    Each AIML category is uniquely identified by its pattern path, which
    consists of the pattern, that and topic elements. The GraphMaster stores
    the corresponding template node in such a way, that it can be retrieved
    by the `match` method iff the input path matches the pattern path.

    Typical order of operations over graphmaster consists of:
        a) storing categories:
            I) validate - make sure the category conforms the AIML
                specification and/or the available tag
            II) save(category)
        b) retrieving: - realized via match()
    """

    # constants for creating pattern and input path
    THAT = "__THAT__"
    TOPIC = "__TOPIC__"

    def __init__(self, bot_config: 'BotConfig',
                 policy: Union[str, PolicyFn] = KEEP_LAST_POLICY):
        """
        Create a graphmaster.

        :param bot_config: bot configuration file with sets and bot properties
        :param policy: either callable, in which case it should accept
        two objects stored in the graphmaster that have same path, and
        return one object (merged object) of the same type;
        or string - one of the following:

            - `keep_first`: when merging, the first stored object is kept,
            - `keep_last`: same, but keeps only the last object.

        The only requirements for the callable is that it is not a lambda.
        """
        self.bot_config = bot_config
        self.root = GMNode()
        self._size = 0
        self.merge_policy = _resolve_policy(policy)
        self._known_patterns: List[Pattern] = []  # sorted by priority

    def add_pattern_tag(self, tag: Pattern):
        """Add pattern tag to the known tags of this graphmaster.

        If the same priority tag is present, this tag will be matched
        first.
        """
        _insort(tag, self._known_patterns, key=lambda p: -p.priority)

    def validate(self, category: Category, logger: Logger) -> None:
        """
        Validate the category, check its syntax.

        Make sure the pattern, that and topic tags contain valid elements.
        The validation results are stored in the `logger` instance.

        Calling this function successfully (without errors in the logger) is
        a precondition of storing objects based on this category into this
        graphmaster.

        :param category: category to validate
        :param logger: logger to log errors or warning
        :returns: nothing, use logger to check for errors
        """
        for node in (category.pattern, category.that, category.topic):
            if node is None:
                assert node is not category.pattern
                continue
            for child in node.children:
                recognised = False
                for p in self._known_patterns:
                    if p.recognises(child):
                        p.parse(child, logger)
                        recognised = True
                        break
                if not recognised:
                    logger.error(child, "unknown pattern path: " + str(child))

    def _make_path(self, cat: Category) -> List[Node]:
        """
        Construct a pattern path from the `Category` object.

        The parts of the category are split on spaces, or tag boundaries.
        The <pattern> must be non-empty.

        The pattern path is a sequence of nodes:

                pattern - __THAT__ - that - __TOPIC__ - topic

        witch multi-word phrases split into the individual words, so
        that `Pattern` can match them.
        """
        def split(n: Node):
            if not n.is_text_node:
                return [n]
            assert n.text is not None
            return map(
                lambda t: Node.Value(t, n, n.filename,
                                     n.line, n.col,
                                     n.aiml_version),
                n.text.upper().split()
            )

        path = []
        for x in cat.pattern.children:
            path.extend(split(x))
        for node, text in zip([cat.that, cat.topic], [self.THAT, self.TOPIC]):
            path.append(Node.Value(text, None, None, None))
            if node is None:
                path.append(Node.Value("*", cat.pattern, cat.pattern.filename))
            else:
                for x in node.children:
                    path.extend(split(x))
        return path

    def save_obj(self, obj: StoredObj) -> Any:
        """
        Store `obj` and return its stored representation.

        For example id which will be stored in the memory.

        :param obj: the object that should be stored in the graphmaster
        :return: representation of the object saved in-memory
        """
        # default behaviour: store everything in the memory
        return obj

    def save(self, category: Category):
        """
        Save the `category` into the graphmaster.

        Traverse the graphmaster according to the pattern path specified
        by the `category`, creating new nodes if necessary, and store the
        template  on the specified place, so it can be later retrieved
        by `match`.

        Successfully calling `self.validate` is a precondition of correct
        behaviour of this method.

        :param category: a category used to build a pattern path
        """
        gm_node = self.root
        path = self._make_path(category)
        for ast_node in path:
            for p in self._known_patterns:
                if p.recognises(ast_node):
                    gm_node = p.advance(gm_node, ast_node)
                    break
        stored_repr = self.save_obj(category.template)
        if gm_node.obj is None:  # no other category matches the same path
            gm_node.obj = stored_repr
            self._size += 1
        else:
            gm_node.obj = self.merge_policy(gm_node.obj, stored_repr)

    def load_obj(self, stored_representation: Any) -> StoredObj:
        """
        Load the object given its `stored_representation`.

        See ``save_obj`` for more info.

        The following should hold for all x:

            self.save_obj(self.load_obj(x)) = x
            self.load_obj(self.save_obj(x)) = x

        :param stored_representation: representation of object stored in
            the nodemappers
        :return: the real object represented by `stored_representation`
        """
        # default behaviour: we store everything in the memory, without change
        return stored_representation

    def _match_rec(
            self,
            node: GMNode,
            seq: List[str],
            pos: int,
            star_pos: List[Tuple[int, int]],
            matching: List[Tuple[Pattern, int]]
    ) -> Optional[GMNode]:
        """
        Recursively match the sequence starting from `node`.

        :param node: the node to start matching from
        :param seq: sequence of words to match against
        :param pos: index into `sequence` - determines first word to match
        :param star_pos: a list of start and end positions of matched stars,
            should be updated directly
        :param matching: a list with information about which pattern and how
            many words matched
        :return: matched node with the object or None if None matches
        """
        # if we are past the sequence and this node is not a terminal
        # node, that means the matching has failed
        if pos >= len(seq):
            return node if node.obj is not None else None

        # try each known pattern to start matching from the current node
        # in the order of decreasing priority
        for pat_tag in self._known_patterns:
            for next_node, num_words in pat_tag.match(seq, pos, node, self):
                matched_rest = self._match_rec(next_node, seq, pos + num_words,
                                               star_pos, matching)
                if matched_rest is None:
                    # the rest failed to match, backtrack
                    continue
                # otherwise we update the stars and return
                if pat_tag.is_star:
                    star_pos.append((pos, pos + num_words))
                matching.append((pat_tag, num_words))
                return matched_rest
        # if nothing returned before that means that all know_patterns
        # failed to match the input sequence so we return `None`
        return None

    def _resolve_stars(self, match: List[Tuple[Pattern, int]], seq: List[str])\
            -> 'StarBindings':
        """
        From the computed star position, recalculate the stars as they are.

        :param match: matched sequence of nodes, pairs of matched pattern and
            number of matched words
        :param seq: the sequence the matching was done against
        :return: matched star-bindings
        """
        sb = StarBindings()
        pos = 0

        # find position of THAT and TOPIC to correctly update {that,topic}stars
        that, topic = 0, 0
        for i, w in enumerate(seq):
            if w == self.THAT:
                that = i
            elif w == self.TOPIC:
                topic = i

        for p, num in match:
            if p.is_star:
                end = pos + num
                text = " ".join(seq[pos:end])
                if end <= that:
                    sb.stars.append(text)
                elif end <= topic:
                    sb.thatstars.append(text)
                else:
                    sb.topicstars.append(text)
            pos += num
        return sb

    def match(self, input_: str, that_: str, topic_: str) \
            -> Optional[Tuple[StoredObj, StarBindings, List[float]]]:
        """
        Find the matching Pattern Path.

        Given input, that (last bot's response) and topic, construct input path
        and find the matching category, retrieving the stored object with
        the matched stars and a sequence of priorities of matching.

        All the arguments should be already normalized.

        :param input_: user's input
        :param that_: last bot's response
        :param topic_: conversation topic
        :return: None if no matching category was found, else a tuple with
            - [0] matched object saved with the best-matching category
            - [1] star bindings for the matching
            - [2] a sequence of priorities used to find the matching, can be
            used to compare different matching-s (the bigger value and
            sooner, the better match)
        """
        seq = self._create_input_path(input_, that_, topic_)
        star_positions: List[Tuple[int, int]] = []
        matching: List[Tuple[Pattern, int]] = []

        match_node = self._match_rec(self.root, seq, 0, star_positions,
                                     matching)

        # if we didn't match anything, rather then raising exception,
        # we return `None`
        if match_node is None:
            return None

        # the last node is the node that contains the object we are seeking
        stored_repr = match_node.obj
        stored_obj = self.load_obj(stored_repr)

        # `matching` is in the reversed order, as it was updated only
        # after we have found the match, reverse it
        matching = matching[::-1]
        stars = self._resolve_stars(matching, seq)
        return stored_obj, stars, [p.priority for p, _ in matching]

    def _create_input_path(self, input_: str, that_: str, topic_: str) \
            -> List[str]:
        """
        Convert `input_`, `that_` and `topic_` into the Input Path.

        The input path contains of word sequences from user input,
        last bot's reply and current topic. Each word is separated by
        spaces.
        """
        result = input_.split()
        result.append(self.THAT)
        result.extend(that_.split())
        result.append(self.TOPIC)
        result.extend(topic_.split())
        return result

    @staticmethod
    def load(filename: str) -> 'GraphMaster':
        """
        Load the graphmaster from the file, after it was saved using `dump`.

        :param filename: name of the file to load graphmaster from
        :return: loaded graphmaster
        """
        with open(filename, "rb") as f:
            gm = dill.load(f)
            assert isinstance(gm, GraphMaster), "not a graphmaster"
            return gm

    def dump(self, filename: str) -> None:
        """Store the graphmaster into the specified file."""
        with open(filename, "wb") as f:
            dill.dump(self, f)

    def size(self) -> int:
        """Return the number of AIML categories."""
        return self._size

    def vocabulary(self) -> Set[str]:
        """
        Implement <vocabulary> tag.

        Return a set of words this graphmaster understands (including stars,
        excluding any word containing underscores).

        Approximates <vocabulary/> tag in the sense that it does not
        count the words in <set>, as it is undefined how many words
        infinite sets (:number:) have.
        """
        res: Set[str] = set()

        def _is_counted(x: str):
            return "_" not in x and " " not in x

        def _vocabulary(node: GMNode):
            res.update(filter(_is_counted, node.children.keys()))
            for child in node.children.values():
                _vocabulary(child)

        _vocabulary(self.root)
        return res

    def generate_html(self, filename: str, *args, **kwargs):
        """
        Store graphmaster to html file.

        This method can be used for debugging purposes.

        Opens the browser with the generated html. It is necessary that
        `pyvis` library is also installed.

        By default, the graph is directed, 1000 x 1000 px.

        :param filename: name of the file to store generated html into
        :param args: positional arguments passed to `pyvis.network.Network`
        :param kwargs: keyword arguments passed to `pyvis.network.Network`
        :return: the generated graph
        """
        try:
            from pyvis.network import Network
        except ImportError as e:
            raise ValueError("`pyvis` must be installed") from e

        gm_net = Network(directed=True, height='1000px', width='1000px',
                         *args, **kwargs)
        gm_net.barnes_hut()
        gm_net.inherit_edge_colors(False)

        def gen_rec(root: GMNode, prev_id=None, prev_symbol=None):
            shape = "box" if root.obj else "dot"
            gm_net.add_node(id(root), id(root), shape=shape)
            if prev_id:
                gm_net.add_edge(prev_id, id(root), label=prev_symbol)
            for k, v in root.children.items():
                gen_rec(v, id(root), k)

        gen_rec(self.root)
        gm_net.show_buttons()
        gm_net.show(filename)
        return gm_net
