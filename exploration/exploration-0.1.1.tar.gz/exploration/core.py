"""
- Authors: Peter Mawhorter
- Consulted:
- Date: 2022-3-3
- Purpose: Core types and tools for dealing with them.

This file defines the main types used for processing and storing
exploration graphs. Key types are:

- `DecisionGraph`: Represents a graph of decisions, including observed
    connections to unknown destinations.
- `Exploration`: A list of `DecisionGraph`s with position and transition
    information representing exploration over time.
"""

from typing import (
    Any, Optional, List, Set, Union, Iterable, cast, Tuple, Dict,
    TypedDict, Sequence, Collection
)

import copy, ast, sys, warnings, random

from . import graphs

Decision = str
"""
A type alias: decision points are defined by their names.

A decision represents a location within a decision graph where a decision
can be made about where to go, or a dead-end reached by a previous
decision. Typically, one room can have multiple decision points in it,
even though many rooms have only one.
"""

Transition = str
"""
A type alias: transitions are defined by their names.

A transition represents a means of travel from one decision to another.
Outgoing transition names have to be unique at each decision, but not
globally.
"""


State = dict
"""
A type alias: states are just dictionaries.

They can contain whatever key/value pairs are necessary to represent
exploration-relevant game state. Typical entries might include:

- `'powers'`: A set of `Power`s the player has acquired.
- `'tokens'`: A dictionary mapping `Token`s to integers representing how
    many of that token type have been acquired.
"""


Power = str
"""
A type alias: powers are defined by their names.

A power represents a capability that can be used to traverse certain
transitions. These transitions should have a `Requirement` specified to
indicate which power(s) and/or token(s) can be used to traverse it.
Powers are usually permanent, but may in some cases be temporary or be
temporarily disabled. Powers might also combine (e.g., speed booster
can't be used underwater until gravity suit is acquired).
"""

Token = str
"""
A type alias: tokens are defined by their type names.

A token represents an expendable item that can be used to traverse certain
transitions a limited number of times (normally once after which the
token is used up), or to permanently open certain transitions.

When a key permanently opens only one specific door, or is re-usable to
open many doors, that should be represented as a Power, not a token. Only
when there is a choice of which door to unlock (and the key is then used
up) should keys be represented as tokens.
"""

Tag = str
"""
A type alias: tags are strings.

A tag is an arbitrary string attached to a decision or transition.
Meanings are left up to the map-maker, but some conventions include:

- `'random'` indicates that an edge (usually an action, i.e., a
    self-edge) is not always available, but instead has some random
    element to it (for example, a random item drop from an enemy).
    Normally, the specifics of the random mechanism are not represented
    in detail.
- `'hard'` indicates that an edge is non-trivial to navigate. An
    annotation starting with `'fail:'` can be used to name another edge
    which would be traversed instead if the player fails to navigate the
    edge (e.g., a difficult series of platforms with a pit below that
    takes you to another decision). This is of course entirely
    subjective.
- `'false'` indicates that an edge doesn't actually exist, although it
    appears to. This tag is added in the same exploration step that
    requirements are updated (normally to `ReqImpossible`) to indicate
    that although the edge appeared to be traversable, it wasn't. This
    distinguishes that case from a case where edge requirements actually
    change.
- `'error'` indicates that an edge does not actually exist, and it's
    different than `'false'` because it indicates an error on the
    player's part rather than intentional deception by the game (another
    subjective distinction). It can also be used with a colon and another
    tag to indicate that that tag was applied in error (e.g., a ledge
    thought to be too high was not actually too high). This should be
    used sparingly, because in most cases capturing the player's
    perception of the world is what's desired. This is normally applied
    in the step before an edge is removed from the graph.
- `'hidden'` indicates that an edge is non-trivial to perceive. Again
    this is subjective. `'hinted'` can be used as well to indicate that
    despite being obfuscated, there are hints that suggest the edge's
    existence.
- `'internal'` indicates that this transition joins two different parts
    of the same room, which are represented as separate decisions.
- `'created'` indicates that this transition is newly created and
    represents a change to the decision layout. Normally, when entering
    a decision point, all visible options will be listed. When
    revisiting a decision, several things can happen:
        1. You could notice a transition you hadn't noticed before.
        2. You could traverse part of the room that you couldn't before,
           observing new transitions that have always been there (this
           would be represented as an internal edge to another decision
           node).
        3. You could observe that the decision had changed due to some
           action or event, and discover a new transition that didn't
           exist previously.
    This tag distinguishes case 3 from case 1. The presence or absence
    of a `'hidden'` tag in case 1 represents whether the newly-observed
    (but not new) transition was overlooked because it was hidden or was
    just overlooked accidentally.
"""

Annotation = str
"A type alias: annotations are strings."


if sys.version_info < (3, 8):
    AstStrNode = ast.Str
else:
    AstStrNode = ast.Constant
"An AST node representing a string constant (changed in version 3.8)."


class Requirement:
    """
    Represents a precondition for traversing an edge or taking an action.
    This can be any boolean expression over powers and/or tokens the
    player needs to posses, with numerical values for the number of
    tokens required. For example, if the player needs either the
    wall-break power or the wall-jump power plus a balloon token, you
    could represent that using:

        ReqAny(
            ReqPower('wall-break'),
            ReqAll(
                ReqPower('wall-jump'),
                ReqTokens('balloon', 1)
            )
        )

    The subclasses define concrete requirements.
    """
    def satisfied(self, state: State) -> bool:
        """
        This will return True if the requirement is satisfied in the
        given game state, and False otherwise.
        """
        raise NotImplementedError(
            "Requirement is an abstract class and cannot be"
            " used directly."
        )

    def __eq__(self, other: Any) -> bool:
        raise NotImplementedError(
            "Requirement is an abstract class and cannot be compared."
        )

    def asGainList(self) -> List[Union[Power, Tuple[Token, int]]]:
        """
        Transforms this `Requirement` into a list of `Power` and/or
        `Token` entries suitable for the 'gain' slot of a
        `TransitionEffects` dictionary. The requirement must be either a
        `ReqTokens`, a `ReqPower`, or a `ReqAny` which includes only
        those three types as sub-requirements. The token and power
        requirements at the leaves of the tree will be collected into a
        list for the result. Raises a `TypeError` if this requirement is
        not suitable for transformation into a gains list.

        TODO: This code should be distributed to the sub-classes...
        """
        if isinstance(self, ReqPower):
            return [self.power]
        elif isinstance(self, ReqTokens):
            return [ (self.tokenType, self.cost) ]
        elif isinstance(self, ReqAny):
            result = []
            for sub in self.subs:
                result.extend(sub.asGainList())
            return result
        else:
            raise TypeError(
                f"Requirement contains a '{type(self)}' which cannot be"
                f" converted into a gained power or token (only"
                f" ReqPower, ReqTokens, and ReqAny are allowed, meaning"
                f" that '|' must be used instead of '&')."
            )

    @staticmethod
    def parse(req: str) -> 'Requirement':
        """
        This static method takes a string and returns a `Requirement`
        object using a mini-language for specifying requirements. The
        language uses '|' for 'or', '&' for 'and', '*' to indicate a
        token requirement (with an integer afterwards specifying the
        number of tokens) and either a valid Python identifier or a
        quoted string to name a power or token type required. You can
        also use 'X' (without quotes) for a never-satisfied requirement,
        and 'O' (without quotes) for an always-satisfied requirement. In
        particular, 'X' can be used for transitions which are only going
        to become accessible when some event takes place, like when a
        switch is flipped. Finally, you can use '-' for negation of a
        requirement; when applied to a token this flips the sense of the
        integer from 'must have at least this many' to 'must have
        strictly less than this many'.
        """
        # Parse as Python
        try:
            root = ast.parse(req.strip(), '<requirement string>', 'eval')
        except (SyntaxError, IndentationError):
            raise ValueError(f"Could not parse requirement '{req}'.")

        if not isinstance(root, ast.Expression):
            raise ValueError(
                f"Could not parse requirement '{req}'"
                f" (result must be an expression)."
            )

        top = root.body

        if not isinstance(top, (ast.BinOp, ast.Name, AstStrNode)):
            raise ValueError(
                f"Could not parse requirement '{req}'"
                f" (result must use only '|', '&', '*', quotes, and"
                f" parentheses)."
            )

        return Requirement.convertAST(top)

    @staticmethod
    def convertAST(node: ast.expr) -> 'Requirement':
        if isinstance(node, ast.UnaryOp):
            if not isinstance(node.op, ast.USub):
                raise ValueError(
                    f"Invalid unary operator:\n{ast.dump(node)}"
                )
            negated = Requirement.convertAST(node.operand)
            return ReqNot(negated)

        if isinstance(node, ast.BinOp):
            # Three valid ops: '|' for or, '&' for and, and '*' for
            # tokens.
            if isinstance(node.op, ast.BitOr):
                # An either-or requirement
                lhs = Requirement.convertAST(node.left)
                rhs = Requirement.convertAST(node.right)
                # We flatten or-or-or chains
                if isinstance(lhs, ReqAny):
                    lhs.subs.append(rhs)
                    return lhs
                elif isinstance(rhs, ReqAny):
                    rhs.subs.append(lhs)
                    return rhs
                else:
                    return ReqAny([lhs, rhs])

            elif isinstance(node.op, ast.BitAnd):
                # An all-of requirement
                lhs = Requirement.convertAST(node.left)
                rhs = Requirement.convertAST(node.right)
                # We flatten and-and-and chains
                if isinstance(lhs, ReqAll):
                    lhs.subs.append(rhs)
                    return lhs
                elif isinstance(rhs, ReqAll):
                    rhs.subs.append(lhs)
                    return rhs
                else:
                    return ReqAll([lhs, rhs])

            elif isinstance(node.op, ast.Mult):
                # Merge power into token name w/ count
                lhs = Requirement.convertAST(node.left)
                if isinstance(lhs, ReqPower):
                    name = lhs.power
                    negate = False
                elif isinstance(lhs, ReqNot) and isinstance(lhs.sub, ReqPower):
                    name = lhs.sub.power
                    negate = True
                else:
                    raise ValueError(
                        f"Invalid token name:\n{ast.dump(node.left)}"
                    )

                if sys.version_info < (3, 8):
                    if (
                        not isinstance(node.right, ast.Num)
                     or not isinstance(node.right.n, int)
                    ):
                        raise ValueError(
                            f"Invalid token count:\n{ast.dump(node.right)}"
                        )

                    n = node.right.n
                else:
                    if (
                        not isinstance(node.right, ast.Constant)
                     or not isinstance(node.right.value, int)
                    ):
                        raise ValueError(
                            f"Invalid token count:\n{ast.dump(node.right)}"
                        )

                    n = node.right.value

                if negate:
                    return ReqNot(ReqTokens(name, n))
                else:
                    return ReqTokens(name, n)

            else:
                raise ValueError(
                    f"Invalid operator type for requirement:"
                    f" {type(node.op)}"
                )

        elif isinstance(node, ast.Name):
            # variable names are interpreted as power names (with '*'
            # the bin-op level will convert to a token name).
            if node.id == 'X':
                return ReqImpossible()
            elif node.id == 'O':
                return ReqNothing()
            else:
                return ReqPower(node.id)

        elif isinstance(node, AstStrNode):
            # Quoted strings can be used to name powers that aren't
            # valid Python identifiers
            if sys.version_info < (3, 8):
                name = node.s
            else:
                name = node.value

            if not isinstance(name, str):
                raise ValueError(
                    f"Invalid value for requirement: '{name}'."
                )

            return ReqPower(name)

        else:
            raise ValueError(
                f"Invalid AST node for requirement:\n{ast.dump(node)}"
            )


class ReqAny(Requirement):
    """
    A disjunction requirement satisfied when any one of its
    sub-requirements is satisfied.
    """
    def __init__(self, subs: Iterable[Requirement]) -> None:
        self.subs = list(subs)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqAny) and other.subs == self.subs

    def __repr__(self):
        return "ReqAny(" + repr(self.subs) + ")"

    def satisfied(self, state: State) -> bool:
        """
        True as long as any one of the sub-requirements is satisfied.
        """
        return any(sub.satisfied(state) for sub in self.subs)


class ReqAll(Requirement):
    """
    A conjunction requirement satisfied when all of its sub-requirements
    are satisfied.
    """
    def __init__(self, subs: Iterable[Requirement]) -> None:
        self.subs = list(subs)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqAll) and other.subs == self.subs

    def __repr__(self):
        return "ReqAll(" + repr(self.subs) + ")"

    def satisfied(self, state: State) -> bool:
        """
        True as long as all of the sub-requirements are satisfied.
        """
        return all(sub.satisfied(state) for sub in self.subs)


class ReqNot(Requirement):
    """
    A negation requirement satisfied when its sub-requirement is NOT
    satisfied.
    """
    def __init__(self, sub: Requirement) -> None:
        self.sub = sub

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqNot) and other.sub == self.sub

    def __repr__(self):
        return "ReqNot(" + repr(self.sub) + ")"

    def satisfied(self, state: State) -> bool:
        """
        True as long as the sub-requirement is not satisfied.
        """
        return not self.sub.satisfied(state)


class ReqPower(Requirement):
    """
    A power requirement satisfied if the specified power is possessed by
    the player according to the given state.
    """
    def __init__(self, power: Power) -> None:
        self.power = power

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqPower) and other.power == self.power

    def __repr__(self):
        return "ReqPower(" + repr(self.power) + ")"

    def satisfied(self, state: State) -> bool:
        return self.power in state["powers"]


class ReqTokens(Requirement):
    """
    A token requirement satisfied if the player possesses at least a
    certain number of a given type of token.

    Note that checking the satisfaction of individual doors in a specific
    state is not enough to guarantee they're jointly traversable, since
    if a series of doors requires the same kind of token, further logic
    is needed to understand that as the tokens get used up, their
    requirements may no longer be satisfied.
    """
    def __init__(self, tokenType: Token, cost: int) -> None:
        self.tokenType = tokenType
        self.cost = cost

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ReqTokens)
        and other.tokenType == self.tokenType
        and other.cost == self.cost
        )

    def __repr__(self):
        return f"ReqTokens({repr(self.tokenType)}, {repr(self.cost)})"

    def satisfied(self, state: State) -> bool:
        return (
            state.setdefault('tokens', {}).get(self.tokenType, 0)
         >= self.cost
        )


class ReqNothing(Requirement):
    """
    A requirement representing that something doesn't actually have a
    requirement. This requirement is always satisfied.
    """
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqNothing)

    def __repr__(self):
        return "ReqNothing()"

    def satisfied(self, state: State) -> bool:
        return True


class ReqImpossible(Requirement):
    """
    A requirement representing that something is impossible. This
    requirement is never satisfied.
    """
    def __eq__(self, other: Any) -> bool:
        return isinstance(other, ReqImpossible)

    def __repr__(self):
        return "ReqImpossible()"

    def satisfied(self, state: State) -> bool:
        return False


class TransitionEffects(TypedDict):
    """
    Represents the effects of a transition on the decision graph and/or
    game state. Can represent the following changes:

    - `'gain'`: a list of `Power`s or (`Token`, amount) pairs
        indicating powers and/or tokens gained.
    - `'lose'`: a list of `Power`s or (`Token`, amount) pairs
        indicating powers and/or tokens lost/spent.
    - `'alters'`: a list of (decision, transition, requirement-string)
        tuples indicating updated requirements for certain
        transitions, which can include removing requirements if None
        is used as the third element.
    - `'tags'`: a list of (decision, taglist) and/or (decision,
        transition, taglist) tuples where the taglist is a list of
        strings each starting with '+' or '-' indicating tags to
        remove or add to that decision or transition.
    - `'next'`: an optional dictionary with all of the same keys,
        including `'next'`, that will replace the original effects once
        the transition's effects have been applied. If None, the effects
        will be discarded once triggered, unless `'cycle'` is set to
        `True`, in which case the effects will remain as-is.
    - `'cycle'`: a boolean indicating whether, once these effects are
        replaced by the `'next'` effects, they should be added as
        `'next'` effects to the current final set of effects in the
        `'next'` chain. If not, once replaced they will be deleted.
    """
    gain: List[Union[Power, Tuple[Token, int]]]
    lose: List[Union[Power, Tuple[Token, int]]]
    alters: List[Tuple[Decision, Transition, Optional[str]]]
    tags: List[
        Union[
            Tuple[Decision, List[str]],
            Tuple[Decision, Transition, List[str]]
        ]
    ]
    next: Any # Support for recursive types when?
    cycle: bool


def mergeEffects(
    a: TransitionEffects,
    b: TransitionEffects
) -> TransitionEffects:
    """
    Merges two transition effects dictionaries according to the
    following rules:
    1. The `gain`, `lose`, and `alters` lists are concatenated, with the
        entries from the first effects object appearing first.
    2. For each decision or transition which includes tags
        added/removed that appears in both effects, those tag lists
        are merged (note that this may result in a tag list which
        applies and then removes a tag, or vice versa, so order
        matters).
    3. The `next` values are merged recursively.
    4. If either effect cycles, the merged effect will too.

    Note that because the next/cycle fields cannot be easily merged,
    this will distort complex effects!

    TODO: Truly modular effects system...
    """
    result: TransitionEffects = {
        'gain': a['gain'] + b['gain'],
        'lose': a['lose'] + b['lose'],
        'alters': a['alters'] + b['alters'],
        'tags': [],
        'next': None,
        'cycle': a['cycle'] or b['cycle']
    }

    # Merge tags: first map tags of b, then add those to spots in a
    bTagMap: Dict[
        Union[Decision, Tuple[Decision, Transition]],
        List[str]
    ] = {}
    for tagIt in b['tags']:
        if len(tagIt) == 2:
            tagIt = cast(Tuple[Decision, List[str]], tagIt)
            bTagMap[tagIt[0]] = tagIt[1]
        else: # length must be 3
            tagIt = cast(Tuple[Decision, Transition, List[str]], tagIt)
            bTagMap[tagIt[0:2]] = tagIt[2]

    # Track what we've seen so we can add extras
    seen: Set[Union[Decision, Tuple[Decision, Transition]]] = set()
    for tagIt in a['tags']:
        if len(tagIt) == 2:
            tagIt = cast(Tuple[Decision, List[str]], tagIt)
            if tagIt[0] in bTagMap:
                result['tags'].append(
                    (tagIt[0], tagIt[1] + bTagMap[tagIt[0]])
                )
                seen.add(tagIt[0])
        else: # length must be 3
            tagIt = cast(Tuple[Decision, Transition, List[str]], tagIt)
            if tagIt[0:2] in bTagMap:
                result['tags'].append(
                    (tagIt[0], tagIt[1], tagIt[2] + bTagMap[tagIt[0:2]])
                )
                seen.add(tagIt[0:2])

    # Add leftovers that don't need merging
    for key in bTagMap:
        if key not in seen:
            if isinstance(key, tuple):
                result['tags'].append((key[0], key[1], bTagMap[key]))
            else:
                result['tags'].append((key, bTagMap[key]))

    # Merge next fields recursively, or take unique next
    if a['next'] is None:
        result['next'] = b['next']
    elif b['next'] is None:
        result['next'] = a['next']
    else:
        result['next'] = mergeEffects(a['next'], b['next'])

    return result


def effects(
    gain: Optional[List[Union[Power, Tuple[Token, int]]]] = None,
    lose: Optional[List[Union[Power, Tuple[Token, int]]]] = None,
    alters: Optional[
        List[Tuple[Decision, Transition, Optional[str]]]
    ] = None,
    tags: Optional[List[Union[
        Tuple[Decision, List[str]],
        Tuple[Decision, Transition, List[str]]
    ]]] = None,
    next: Optional[TransitionEffects] = None,
    cycle: bool = False
) -> TransitionEffects:
    """
    Factory for transition effects which includes default values so you
    can just specify effect types that are relevant to a particular
    situation.
    """
    if gain is None:
        gain = []

    if lose is None:
        lose = []

    if alters is None:
        alters = []

    if tags is None:
        tags = []

    return {
        'gain': gain,
        'lose': lose,
        'alters': alters,
        'tags': tags,
        'next': next,
        'cycle': cycle
    }


class TransitionProperties(TypedDict):
    """
    Represents bundled properties of a transition, including a
    requirement, effects, tags, and/or annotations. Does not include the
    reciprocal. Has the following slots:

    - `'requirement'`: The requirement for the transition. This is
        always a `Requirement`, although it might be `ReqNothing` if
        nothing special is required.
    - `'effects'`: The effects of the transition.
    - `'tags'`: Any tags applied to the transition.
    - `'annotations'`: A list of annotations applied to the transition.
    """
    requirement: Requirement
    effects: TransitionEffects
    tags: Set[Tag]
    annotations: List[Annotation]


def mergeProperties(
    a: TransitionProperties,
    b: TransitionProperties
) -> TransitionProperties:
    """
    Merges two sets of transition properties, following these rules:

    1. Tags and annotations are combined. Annotations from the
        second property set are ordered after those from the first.
    2. If one of the transitions has a `ReqNothing` instance as its
        requirement, we use the other requirement. If both have
        complex requirements, we create a new `ReqAll` which
        combines them as the requirement.
    3. The effects are merged using `mergeEffects`. Note that this can
        seriously change how effects operate (TODO: Fix that)
    """
    result: TransitionProperties = {
        "requirement": ReqNothing(),
        "effects": mergeEffects(a["effects"], b["effects"]),
        "tags": a["tags"] | b["tags"],
        "annotations": a["annotations"] + b["annotations"],
    }

    if a["requirement"] == ReqNothing():
        result["requirement"] = b["requirement"]
    elif b["requirement"] == ReqNothing():
        result["requirement"] = a["requirement"]
    else:
        result["requirement"] = ReqAll(
            [a["requirement"], b["requirement"]]
        )

    return result


RANDOM_NAME_SUFFIXES = False
"""
Causes `uniqueName` to use random suffixes instead of sequential ones,
which is more efficient when many name collisions are expected but which
makes things harder to test and debug. False by default.
"""


def uniqueName(base: str, existing: Collection) -> str:
    """
    Finds a unique name relative to a collection of existing names,
    using the given base name, plus a unique suffix if that base name is
    among the existing names. If the base name isn't among the existing
    names, just returns the base name. The suffix consists of a period
    followed by a number, and the lowest unused number is used every
    time. This does lead to poor performance in cases where many
    collisions are expected; you can set `RANDOM_NAME_SUFFIXES` to True
    to use a random suffix instead.

    Note that if the base name already has a numerical suffix, that
    suffix will be changed instead of adding another one.
    """
    # Short-circuit if we're already unique
    if base not in existing:
        return base

    # Ensure a digit suffix
    if (
        '.' not in base
     or not base.split('.')[-1].isdigit()
    ):
        base += '.1'

    # Find the split point for the suffix
    # This will be the index after the '.'
    splitPoint = len(base) - list(reversed(base)).index('.')
    if not RANDOM_NAME_SUFFIXES:
        suffix = int(base[splitPoint:])

    while base in existing:
        if RANDOM_NAME_SUFFIXES:
            base = base[:splitPoint] + str(random.randint(0, 1000000))
        else:
            suffix += 1
            base = base[:splitPoint] + str(suffix)

    return base


class DecisionGraph(graphs.UniqueExitsGraph):
    """
    Represents a view of the world as a topological graph at a moment in
    time. It derives from `networkx.MultiDiGraph`.

    Each node (a `Decision`) represents a place in the world where there
    are multiple opportunities for travel/action, or a dead end where
    you must turn around and go back; typically this is a single room in
    a game, but sometimes one room has multiple decision points. Edges
    (`Transition`s) represent choices that can be made to travel to
    other decision points (e.g., taking the left door), or when they are
    self-edges, they represent actions that can be taken within a
    location that affect the world or the game state.

    Each `Transition` includes a `TransitionEffects` dictionary
    indicating the effects that it has. Other effects of the transition
    that are not simple enough to be included in this format may be
    represented in an `Exploration` by changing the graph in the next step
    to reflect further effects of a transition.

    In addition to normal edges between nodes, a `DecisionGraph` can
    represent potential edges which lead to unknown destinations. These
    are represented by adding nodes whose names begin with `'_u:'`, with
    a separate unknown node for each edge. These unknown edges are
    tagged `'unknown'`.

    Both nodes and edges can have `Annotation`s associated with them that
    include extra details about the explorer's perception of the
    situation. They can also have `Tag`s, which represent specific
    categories an transition or decision falls into.
    """
    def __init__(self) -> None:
        super().__init__()
        self.unknownCount = 0

    def decisionActions(self, decision: Decision) -> Set[Transition]:
        """
        Retrieves the set of self-edges at a decision. Editing the set
        will not affect the graph.
        """
        return set(self.edges[decision, decision])

    def getTransitionProperties(
        self,
        decision: Decision,
        transition: Transition
    ) -> TransitionProperties:
        """
        Returns a dictionary containing transition properties for the
        specified transition from the specified decision. The properties
        included are:

        - 'requirement': The requirement for the transition.
        - 'effects': Any effects of the transition.
        - 'tags': Any tags applied to the transition.
        - 'annotations': Any annotations on the transition.

        The reciprocal of the transition is not included.
        """
        return {
            'requirement':
                self.getTransitionRequirement(decision, transition),
            'effects': self.getTransitionEffects(decision, transition),
            'tags': self.transitionTags(decision, transition),
            'annotations': self.transitionAnnotations(decision, transition)
        }

    def setTransitionProperties(
        self,
        decision: Decision,
        transition: Transition,
        requirement: Optional[Requirement] = None,
        effects: Optional[TransitionEffects] = None,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None
    ) -> None:
        """
        Sets one or more transition properties all at once. Can be used
        to set the requirement, effects, tags, and/or annotations. Old
        values are overwritten, although if `None`s are provided (or
        arguments are omitted), corresponding properties are not updated.

        To add tags or annotations to existing tags/annotations instead
        of replacing them, use `tagTransition` or `annotateTransition`
        instead.
        """
        if requirement is not None:
            self.setTransitionRequirement(decision, transition, requirement)
        if effects is not None:
            self.setTransitionEffects(decision, transition, effects)
        if tags is not None:
            dest = self.destination(decision, transition)
            self.edges[decision, dest, transition]['tags'] = tags
        if annotations is not None:
            dest = self.destination(decision, transition)
            self.edges[decision, dest, transition]['ann'] = annotations

    def getTransitionRequirement(
        self,
        decision: Decision,
        transition: Transition
    ) -> Requirement:
        """
        Returns the `Requirement` for accessing a specific transition at
        a specific decision. For transitions which don't have
        requirements, returns a `ReqNothing` instance.
        """
        dest = self.destination(decision, transition)

        info = self.edges[decision, dest, transition]

        return info.get('requires', ReqNothing())

    def setTransitionRequirement(
        self,
        decision: Decision,
        transition: Transition,
        requirement: Union[Requirement, str, None]
    ) -> None:
        """
        Sets the `Requirement` for accessing a specific transition at
        a specific decision. Raises a `KeyError` if the decision or
        transition does not exist.

        Deletes the requirement if `None` is given as the requirement;
        if a string is provided, converts it into a `Requirement` using
        `Requirement.parse`. Does not raise an error if deletion is
        requested for a non-existent requirement, and silently
        overwrites any previous requirement.
        """
        dest = self.destination(decision, transition)

        info = self.edges[decision, dest, transition]

        if isinstance(requirement, str):
            requirement = Requirement.parse(requirement)

        if requirement is None:
            try:
                del info['requires']
            except KeyError:
                pass
        else:
            if not isinstance(requirement, Requirement):
                raise TypeError(
                    f"Invalid requirement type: {type(requirement)}"
                )

            info['requires'] = requirement

    def getTransitionEffects(
        self,
        decision: Decision,
        transition: Transition
    ) -> TransitionEffects:
        """
        Retrieves the effects of a transition.

        A `KeyError` is raised if the specified decision/transition
        combination doesn't exist.
        """
        dest = self.destination(decision, transition)

        info = self.edges[decision, dest, transition]

        # Making this explicit allows type-checking it
        default: TransitionEffects = {
            'gain': [],
            'lose': [],
            'alters': [],
            'tags': [],
            'next': None,
            'cycle': True
        }

        return info.get('effects', default)

    def setTransitionEffects(
        self,
        decision: Decision,
        transition: Transition,
        effects: TransitionEffects
    ) -> None:
        """
        Replaces the transition effects for the given transition at the
        given decision. Any previous effects are discarded. See
        `TransitionEffects` for the structure of these. Note that for
        this method, a string can be given in place of a `Requirement`
        and it will be converted using `Requirement.parse`. If `None` is
        given as the requirement, the requirement will not be changed,
        to remove the requirement, explicitly provide a `ReqNothing`
        instance as the `requires` value.

        A `KeyError` is raised if the specified decision/transition
        combination doesn't exist.
        """
        dest = self.destination(decision, transition)

        info = self.edges[decision, dest, transition]

        info['effects'] = effects

    def addAction(
        self,
        decision: Decision,
        action: Transition,
        requires: Union[Requirement, str, None] = None,
        effects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds the given action as a possibility at the given decision. An
        action is just a self-edge, which can have requirements like any
        edge, and which can have effects like any edge.
        The optional arguments are given to `setTransitionRequirement`
        and `setTransitionEffects`; see those functions for descriptions
        of what they mean.

        Raises a `KeyError` if a transition with the given name already
        exists at the given decision.
        """
        self.add_edge(decision, decision, action)
        self.setTransitionRequirement(decision, action, requires)
        if effects is not None:
            self.setTransitionEffects(decision, action, effects)

    def tagDecision(
        self,
        decision: Decision,
        tagOrTags: Union[Tag, Set[Tag]]
    ) -> None:
        """
        Adds a tag (or many tags from a set of tags) to a decision.
        """
        if isinstance(tagOrTags, Tag):
            tagOrTags = { tagOrTags }

        tagsAlready = self.nodes[decision].setdefault('tags', set())
        for tag in tagOrTags:
            tagsAlready.add(tag)

    def untagDecision(self, decision: Decision, tag: Tag) -> None:
        """
        Removes a tag from a decision. Raises a `KeyError` if the
        specified tag is not already present on the specified decision.
        """
        self.nodes[decision]['tags'].remove(tag)

    def decisionTags(self, decision: Decision) -> Set[Tag]:
        """
        Returns the set of tags for a decision. Edits will be applied to
        the graph.
        """
        return self.nodes[decision]['tags']

    def annotateDecision(
        self,
        decision: Decision,
        annotationOrAnnotations: Union[Annotation, Sequence[Annotation]]
    ) -> None:
        """
        Adds an annotation to a decision's annotations list.
        """
        if isinstance(annotationOrAnnotations, Annotation):
            annotationOrAnnotations = [ annotationOrAnnotations ]
        self.nodes[decision]['ann'].extend(annotationOrAnnotations)

    def decisionAnnotations(self, decision: Decision) -> List[Annotation]:
        """
        Returns the list of annotations for the specified decision.
        Modifying the list affects the graph.
        """
        return self.nodes[decision]['ann']

    def tagTransition(
        self,
        decision: Decision,
        transition: Transition,
        tagOrTags: Union[Tag, Set[Tag]]
    ) -> None:
        """
        Adds a tag (or each tag from a set) to a transition coming out of
        a specific decision.
        """
        dest = self.destination(decision, transition)
        if isinstance(tagOrTags, Tag):
            tagOrTags = { tagOrTags }

        tagsAlready = self.edges[decision, dest, transition].setdefault(
            'tags',
            set()
        )
        for tag in tagOrTags:
            tagsAlready.add(tag)

    def untagTransition(
        self,
        decision: Decision,
        transition: Transition,
        tagOrTags: Union[Tag, Set[Tag]]
    ) -> None:
        """
        Removes a tag (or each tag in a set) from a transition coming out
        of a specific decision. Raises a `KeyError` if (one of) the
        specified tag(s) is not currently applied to the specified
        transition.
        """
        dest = self.destination(decision, transition)
        if isinstance(tagOrTags, Tag):
            tagOrTags = { tagOrTags }

        tagsAlready = self.edges[decision, dest, transition].setdefault(
            'tags',
            set()
        )
        for tag in tagOrTags:
            tagsAlready.remove(tag)

    def transitionTags(
        self,
        decision: Decision,
        transition: Transition
    ) -> Set[Tag]:
        """
        Returns the set of tags for a transition. Edits will be applied
        to the graph.
        """
        dest = self.destination(decision, transition)
        return self.edges[decision, dest, transition]['tags']

    def annotateTransition(
        self,
        decision: Decision,
        transition: Transition,
        annotationS: Union[Annotation, Sequence[Annotation]]
    ) -> None:
        """
        Adds an annotation (or a sequence of annotations) to a
        transition's annotations list.
        """
        dest = self.destination(decision, transition)
        if isinstance(annotationS, Annotation):
            annotationS = [ annotationS ]
        self.edges[decision, dest, transition]['ann'].extend(annotationS)

    def transitionAnnotations(
        self,
        decision: Decision,
        transition: Transition
    ) -> List[Annotation]:
        """
        Returns the annotation list for a specific transition at a
        specific decision. Editing the list affects the graph.
        """
        dest = self.destination(decision, transition)
        return self.edges[decision, dest, transition]['ann']

    def transitionReciprocal(
        self,
        decision: Decision,
        transition: Transition
    ) -> Optional[Transition]:
        """
        Returns the reciprocal edge for the specified transition from the
        specified decision (see `setTransitionReciprocal`). Returns
        `None` if no reciprocal has been established for that
        transition, or if that decision or transition does not exist.
        """
        dest = self.getDestination(decision, transition)
        if dest is not None:
            return self.edges[decision, dest, transition].get("reciprocal")
        else:
            return None

    def setTransitionReciprocal(
        self,
        decision: Decision,
        transition: Transition,
        reciprocal: Optional[Transition],
        setBoth: bool = True
    ) -> None:
        """
        Sets the 'reciprocal' transition for a particular transition from
        a particular decision.

        Raises a `KeyError` if the specified decision or transition does
        not exist.

        Raises a `ValueError` if the reciprocal transition does not
        exist, or if it does exist but does not lead back to the
        decision the transition came from.

        If `setBoth` is True (the default) then the transition which is
        being identified as a reciprocal will also have its reciprocal
        property set, pointing back to the primary transition being
        modified.

        If the `reciprocal` value is None, this deletes the reciprocal
        value entirely, and if `setBoth` is true, it does this for the
        previous reciprocal edge as well. No error is raised in this case
        when there was not already a reciprocal to delete. No
        `ValueError`s will be raised in this case either.

        Note that one should remove a reciprocal relationship before
        redirecting either edge of the pair in a way that gives it a new
        reciprocal, since otherwise, a later attempt to remove the
        reciprocal with `setBoth` set to True (the default) will end up
        deleting the reciprocal information from the other edge that was
        already modified. There is no way to reliably detect and avoid
        this, because two different decisions could (and often do in
        practice) have transitions with identical names, meaning that the
        reciprocal value will still be the same, but it will indicate a
        different edge in virtue of the destination of the edge changing.
        """
        dest = self.destination(decision, transition) # possible KeyError
        rdest = self.getDestination(dest, reciprocal)

        # Set or delete reciprocal property
        if reciprocal is None:
            # Delete the property
            old = self.edges[decision, dest, transition].pop('reciprocal')
            if setBoth and self.getDestination(dest, old) is not None:
                # Note this happens even if rdest is != destination!
                del self.edges[dest, decision, old]['reciprocal']
        else:
            # Set the property, checking for errors first
            if rdest is None:
                raise ValueError(
                    f"Reciprocal transition '{reciprocal}' for transition"
                    f" '{transition}' from decision '{decision}' does not"
                    f" exist in decision '{dest}'."
                )

            if rdest != decision:
                raise ValueError(
                    f"Reciprocal transition '{reciprocal}' from decision"
                    f" '{dest}' does not lead back to decision '{decision}'."
                )

            self.edges[decision, dest, transition]['reciprocal'] = reciprocal
            if setBoth:
                self.edges[dest, decision, reciprocal]['reciprocal'] = \
                    transition

    def isUnknown(self, decision: Decision) -> bool:
        """
        Returns True if the specified decision is an 'unknown' decision
        (i.e., if its name starts with '_u:') and False otherwise. These
        decisions represent unknown territory rather than a real visited
        part of the graph.
        """
        return decision.startswith('_u:')

    def addDecision(
        self,
        name: Decision,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None
    ) -> None:
        """
        Adds a decision to the graph, without any transitions yet. Each
        decision needs a unique name. A set of tags and/or a list of
        annotations (strings in both cases) may be provided.

        Raises a ValueError if a decision with the provided name already
        exists (decision names must be unique).
        """
        # Defaults
        if tags is None:
            tags = set()
        if annotations is None:
            annotations = []

        # Error checking
        if name in self:
            raise ValueError(
                f"Cannot add decision '{name}': That decision already"
                f" exists."
            )

        # Add the decision
        self.add_node(name, tags=tags, ann=annotations)

    def addConnectingEdge(
        self,
        fromDecision: Decision,
        name: Transition,
        toDecision: Decision,
        revName: Optional[Transition] = None,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None,
        revTags: Optional[Set[Tag]] = None,
        revAnnotations: Optional[List[Annotation]] = None,
        requires: Union[Requirement, str, None] = None,
        effects: Optional[TransitionEffects] = None,
        revRequires: Union[Requirement, str, None] = None,
        revEffects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds an edge connecting two decisions. The name of each decision
        is required, as is a name for the edge. If a `revName` is
        provided, a reciprocal edge will be added in the opposite
        direction using that name; by default only the specified edge is
        added. A `KeyError` will be raised if the `revName` matches the
        name of an existing edge at the destination decision.

        Both decisions must already exist, or a `ValueError` will be
        raised.

        A set of tags and/or a list of annotations (strings in both
        cases) may be provided. Tags and/or annotations for the reverse
        edge may also be specified if one is being added.

        The `requires`, `effects`, `revRequires`, and `revEffects`
        arguments specify requirements and/or effects of the new outgoing
        and reciprocal edges.
        """
        # Defaults
        if tags is None:
            tags = set()
        if annotations is None:
            annotations = []
        if revTags is None:
            revTags = set()
        if revAnnotations is None:
            revAnnotations = []

        # Error checking
        if fromDecision not in self:
            raise ValueError(
                f"Cannot add a transition from '{fromDecision}' to"
                f" '{toDecision}': '{fromDecision}' does not exist."
            )

        if toDecision not in self:
            raise ValueError(
                f"Cannot add a transition from '{fromDecision}' to"
                f" '{toDecision}': '{toDecision}' does not exist."
            )

        # Note: have to check this first so we don't add the forward edge
        # and then error out after a side effect!
        if (
            revName is not None
        and self.getDestination(toDecision, revName) is not None
        ):
            raise KeyError(
                f"Cannot add a transition from '{fromDecision}' to"
                f" '{toDecision}' with reciprocal edge '{revName}':"
                f" '{revName}' is already used as an edge name at"
                f" '{toDecision}'."
            )

        self.add_edge(
            fromDecision,
            toDecision,
            key=name,
            tags=tags,
            ann=annotations
        )
        self.setTransitionRequirement(fromDecision, name, requires)
        if effects is not None:
            self.setTransitionEffects(fromDecision, name, effects)
        if revName is not None:
            self.add_edge(
                toDecision,
                fromDecision,
                key=revName,
                tags=revTags,
                ann=revAnnotations
            )
            self.setTransitionReciprocal(fromDecision, name, revName)
            self.setTransitionRequirement(toDecision, revName, revRequires)
            if revEffects is not None:
                self.setTransitionEffects(toDecision, revName, revEffects)

    def addUnexploredEdge(
        self,
        fromDecision: Decision,
        name: Transition,
        reciprocal: bool = True,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None,
        revTags: Optional[Set[Tag]] = None,
        revAnnotations: Optional[List[Annotation]] = None,
        requires: Union[Requirement, str, None] = None,
        effects: Optional[TransitionEffects] = None,
        revRequires: Union[Requirement, str, None] = None,
        revEffects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds an edge connecting to a new decision named `'_u:-n-'` where
        '-n-' is the next unused unknown-decision number. This represents
        a transition to an unknown destination. Also adds a reciprocal
        edge in the reverse direction, unless `reciprocal` is set to
        `False`. The reciprocal edge will use the name 'return'.

        The starting decision must already exist, and must not already
        have a transition with the given name, or a ValueError will be
        raised.

        Lists of tags and/or annotations (strings in both cases) may be
        provided. These may also be provided for the reciprocal edge.

        Similarly , requirements and/or effects for either edge may be
        provided.
        """
        # Defaults
        if tags is None:
            tags = set()
        if annotations is None:
            annotations = []
        if revTags is None:
            revTags = set()
        if revAnnotations is None:
            revAnnotations = []

        # Error checking
        if fromDecision not in self:
            raise ValueError(
                f"Cannot add a new unexplored edge '{name}' to"
                f" '{fromDecision}': That decision does not exist."
            )

        if name in self.destinationsFrom(fromDecision):
            raise ValueError(
                f"Cannot add a new edge '{name}': '{fromDecision}'"
                f" already has an outgoing edge with that name."
            )

        # Create the new unexplored decision and add the edge
        toName = '_u:' + str(self.unknownCount)
        self.unknownCount += 1
        self.add_node(toName, tags={'unknown'}, ann=[])
        self.add_edge(
            fromDecision,
            toName,
            key=name,
            tags=tags,
            ann=annotations
        )
        self.setTransitionRequirement(fromDecision, name, requires)
        if effects is not None:
            self.setTransitionEffects(fromDecision, name, effects)

        # Create the reciprocal edge
        if reciprocal:
            self.add_edge(
                toName,
                fromDecision,
                key='return',
                tags=revTags,
                ann=revAnnotations
            )
            self.setTransitionRequirement(toName, 'return', revRequires)
            if revEffects is not None:
                self.setTransitionEffects(toName, 'return', revEffects)
            # Set as a reciprocal
            self.setTransitionReciprocal(fromDecision, name, 'return')

    def retargetTransition(
        self,
        fromDecision: Decision,
        transition: Transition,
        newDestination: Decision,
        swapReciprocal=True,
        errorOnNameColision=True
    ) -> None:
        """
        Given a particular destination and a transition at that
        destination, changes that transition so that it goes to the
        specified new destination instead of wherever it was connected
        to before. If the new destination is the same as the old one, no
        changes are made.

        If `swapReciprocal` is set to True (the default) then any
        reciprocal edge at the old destination will be deleted, and a
        new reciprocal edge from the new destination with equivalent
        properties to the original reciprocal will be created, pointing
        to the origin of the specified transition. If `swapReciprocal`
        is set to False, then the reciprocal relationship with any old
        reciprocal edge will be removed, but the old reciprocal edge
        will not be changed.

        Note that if `errorOnNameColision` is True (the default), then
        if the reciprocal transition has the same name as a transition
        which already exists at the new destination node, a `ValueError`
        will be thrown. However, if it is set to False, the reciprocal
        transition will be renamed with a suffix to avoid any possible
        name collisions.

        ## Example:

        >>> m = DecisionGraph()
        >>> m.add_edges_from([
        ...     ('A', 'B', 'up'),
        ...     ('A', 'B', 'up2'),
        ...     ('B', 'A', 'down'),
        ...     ('B', 'B', 'self'),
        ...     ('B', 'C', 'next'),
        ...     ('C', 'B', 'prev')
        ... ])
        >>> m.setTransitionReciprocal('A', 'up', 'down')
        >>> m.destination('A', 'up')
        'B'
        >>> m.destination('B', 'down')
        'A'
        >>> m.retargetTransition('A', 'up', 'C')
        >>> m.destination('A', 'up')
        'C'
        >>> m.getDestination('B', 'down') is None
        True
        >>> m.destination('C', 'down')
        'A'
        >>> m.add_edge('A', 'B', 'next')
        >>> m.add_edge('B', 'A', 'prev')
        >>> m.setTransitionReciprocal('A', 'next', 'prev')
        >>> # Can't swap a reciprocal in a way that would collide names
        >>> m.retargetTransition('C', 'prev', 'A')
        Traceback (most recent call last):
        ...
        ValueError...
        >>> m.retargetTransition('C', 'prev', 'A', swapReciprocal=False)
        >>> m.destination('C', 'prev')
        'A'
        >>> m.destination('A', 'next') # not changed
        'B'
        >>> # Reciprocal relationship is severed:
        >>> m.transitionReciprocal('C', 'prev') is None
        True
        >>> m.transitionReciprocal('B', 'next') is None
        True
        >>> # Swap back so we can do another demo
        >>> m.retargetTransition('C', 'prev', 'B', swapReciprocal=False)
        >>> m.setTransitionReciprocal('C', 'prev', 'next')
        >>> # Swap reciprocal by renaming it
        >>> m.retargetTransition('C', 'prev', 'A', errorOnNameColision=False)
        >>> m.transitionReciprocal('C', 'prev')
        'next.1'
        >>> m.destination('C', 'prev')
        'A'
        >>> m.destination('A', 'next.1')
        'C'
        >>> m.destination('A', 'next')
        'B'
        >>> # Note names are the same but these are from different nodes
        >>> m.transitionReciprocal('A', 'next')
        'prev'
        >>> m.transitionReciprocal('A', 'next.1')
        'prev'
        """
        # Figure out the old destination of the transition we're swapping
        oldDestination = cast(
            Decision,
            self.destination(fromDecision, transition)
        )

        # If thew new destination is the same, we don't do anything!
        if oldDestination == newDestination:
            return

        # First figure out reciprocal business so we can error out
        # without making changes if we need to 
        if swapReciprocal:
            reciprocal = self.transitionReciprocal(fromDecision, transition)
            if reciprocal is not None:
                targetDestinations = self.destinationsFrom(newDestination)
                collision = reciprocal in targetDestinations
                if collision:
                    if swapReciprocal and errorOnNameColision:
                        raise ValueError(
                            f"Cannot retarget transition '{transition}'"
                            f" from '{fromDecision}': reciprocal"
                            f" transition '{reciprocal}' would be a"
                            f" duplicate transition name at the new"
                            f" destination '{newDestination}'."
                        )
                    else:
                        # Figure out a good fresh reciprocal name
                        newReciprocal = uniqueName(
                            reciprocal,
                            targetDestinations
                        )
                else:
                    newReciprocal = reciprocal
        else:
            reciprocal = None

        # Handle the forward transition...
        # Find the transition properties
        tProps = self.getTransitionProperties(fromDecision, transition)

        # Delete the edge
        self.removeEdgeByKey(fromDecision, transition)

        # Add the new edge
        self.add_edge(fromDecision, newDestination, transition)

        # Reapply the transition properties
        self.setTransitionProperties(fromDecision, transition, **tProps)

        # Handle the reciprocal transition if there is one...
        if reciprocal is not None:
            if not swapReciprocal:
                # Then sever the relationship
                self.setTransitionReciprocal(
                    oldDestination,
                    reciprocal,
                    None,
                    setBoth=False # Other transition was deleted already
                )
            else:
                # Otherwise swap the reciprocal edge
                rProps = self.getTransitionProperties(
                    oldDestination,
                    reciprocal
                )
                self.removeEdgeByKey(oldDestination, reciprocal)
                self.add_edge(newDestination, fromDecision, newReciprocal)
                self.setTransitionProperties(
                    newDestination,
                    newReciprocal,
                    **rProps
                )
                # Establish new reciprocal relationship
                self.setTransitionReciprocal(
                    fromDecision,
                    transition,
                    newReciprocal
                )

    def replaceUnexplored(
        self,
        fromDecision: Decision,
        transition: Transition,
        connectTo: Decision,
        revName: Optional[Transition] = None,
        requirement: Optional[Requirement] = None,
        applyEffects: Optional[TransitionEffects] = None,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None,
        revRequires: Union[Requirement, str, None] = None,
        revEffects: Optional[TransitionEffects] = None,
        revTags: Optional[Set[Tag]] = None,
        revAnnotations: Optional[List[Annotation]] = None,
        decisionTags: Optional[Set[Tag]] = None,
        decisionAnnotations: Optional[List[Annotation]] = None
    ) -> None:
        """
        Given a decision and an edge name in that decision, where the
        named edge leads to an unexplored decision, replaces the `'_u:'`
        decision on the other end of that edge with either a new decision
        using the given `connectTo` name, or if that node already exists,
        with that node. If a `revName` is provided, a reciprocal edge
        will be added using that name connecting the `connectTo` decision
        back to the original decision. If this transition already exists,
        it must also point to an unexplored node, which will also be
        merged into the fromDecision node.

        Any additional edges pointing to or from the unknown node(s)
        being replaced will also be re-targeted at the now-discovered
        known destination(s). These edges will retain their reciprocal
        names, or if this would cause a name clash, a `ValueError` will
        be raised.

        A `ValueError` will be raised if the destination of the specified
        transition is not an unknown decision (see `isUnknown`), or if
        the `connectTo`'s `revName` transition does not lead to an
        unknown decision (it's okay if this second transition doesn't
        exist).

        The transition properties (requirement and/or effects) of the
        replaced transition will be copied over to the new transition,
        except that the 'unknown' tag will be removed. Transition
        properties from the reciprocal transition will also be copied for
        the newly created reciprocal edge. Properties for any additional
        edges to/from the unknown node will also be copied.

        Also, any transition properties on existing forward or reciprocal
        edges from the destination node with the indicated reverse name
        will be merged with those from the target transition. Note that
        this merging process may introduce corruption of complex
        transition effects. TODO: Fix that!

        Any tags and annotations are added to copied tags/annotations,
        but specified requirements, and/or effects will replace previous
        requirements/effects, rather than being added to them.

        ## Example

        >>> TODO
        """
        if tags is None:
            tags = set()
        if annotations is None:
            annotations = []
        if revTags is None:
            revTags = set()
        if revAnnotations is None:
            revAnnotations = []
        if decisionTags is None:
            decisionTags = set()
        if decisionAnnotations is None:
            decisionAnnotations = []

        # Figure out destination decision
        oldUnknown = cast(
            Decision,
            self.destination(fromDecision, transition)
        )

        if not self.isUnknown(oldUnknown):
            raise ValueError(
                f"Transition '{transition}' from '{fromDecision}' does"
                f" not lead to an unexplored region (it leads to"
                f" '{oldUnknown}')."
            )

        # Apply any new tags or annotations, or create a new node
        if connectTo in self:
            self.tagDecision(connectTo, decisionTags)
            self.annotateDecision(connectTo, decisionAnnotations)
        else:
            self.add_node(
                connectTo,
                tags=decisionTags,
                ann=decisionAnnotations
            )

        # Find all edges that point to the node we're replacing, and
        # create copies of them that point to the new destination.
        for source, incomming in self.allEdgesTo(oldUnknown):
            # Find reciprocal edge name going out from this unknown node
            outgoing = self.transitionReciprocal(source, incomming)

            # Capture old transition properties so we can apply them to
            # the new edge we're about to create
            tProps = self.getTransitionProperties(source, incomming)

            # Capture old reciprocal transition properties
            rProps = None
            if outgoing is not None:
                rProps = self.getTransitionProperties(oldUnknown, outgoing)

            # TODO: HERE...

        # Now that we've duplicated all old transitions, we remove the
        # old decision entirely, including all incident edges
        self.remove_node(oldUnknown)

        self.add_edge(
            fromDecision,
            connectTo,
            transition
        )

        # We might find more transition properties we want to
        # preserve...
        extraRevProps: Optional[TransitionProperties] = None
        extraRevRevProps: Optional[TransitionProperties] = None

        # Add reciprocal edge if requested
        if revName is not None:
            oldRevDest = self.getDestination(connectTo, revName)

            # If our existing return edge does not connect to an unknown
            # node, that's a problem
            if oldRevDest is not None:
                oldRevDest = cast(Decision, oldRevDest)
                if not self.isUnknown(oldRevDest):
                    raise ValueError(
                        f"While replacing unknown transition"
                        f" '{transition}' from '{fromDecision}'"
                        f" transition '{revName}' from '{connectTo}'"
                        f" was specified as the reverse connection, but"
                        f" that transition already exists and does not"
                        f" lead to an unknown node."
                    )

                # Ensure that there's only one or two edges here
                if self.degree(oldRevDest) not in (1, 2):
                    raise RuntimeError(
                        f"Unknown decision '{oldReciprocal}' had more"
                        f" than one or two transitions at replacement"
                        f" time."
                    )

                # Capture properties of the other reciprocal transition
                # These have
                extraRevProps = self.getTransitionProperties(
                    connectTo,
                    revName
                )
                otherRev = self.transitionReciprocal(connectTo, revName)
                if otherRev is not None:
                    extraRevRevProps = self.getTransitionProperties(
                        oldRevDest,
                        otherRev
                    )
                else:
                    extraRevRevProps = {
                        "requirement": ReqNothing(),
                        "effects": effects(),
                        "tags": set(),
                        "annotations": []
                    }

                # Remove the old reverse-edge destination node
                # This also deletes its edges
                self.remove_node(oldRevDest)

            # Add new edge connecting back
            self.add_edge(
                connectTo,
                fromDecision,
                revName
            )

            # Copy old reciprocal properties if there were any, and
            # merge properties from both
            if rProps is not None or extraRevProps is not None:
                # Merge if both aren't None
                if rProps is not None and extraRevProps is not None:
                    rProps = mergeProperties(rProps, extraRevProps)
                elif rProps is None:
                    # Otherwise swap so rProps is always the one that
                    # we've found
                    rProps = extraRevProps

                # At this point rProps can't be None any more
                rProps = cast(TransitionProperties, rProps)

                self.setTransitionProperties(connectTo, revName, **rProps)

            # Remove 'unknown' tag
            try:
                self.untagTransition(connectTo, revName, 'unknown')
            except KeyError:
                pass

            # Add explicit tags/annotations and replace
            # requirement/effects
            self.tagTransition(connectTo, revName, revTags)
            self.annotateTransition(connectTo, revName, revAnnotations)
            if revRequires is not None:
                self.setTransitionRequirement(
                    connectTo,
                    revName,
                    revRequires
                )
            if revEffects is not None:
                self.setTransitionEffects(connectTo, revName, revEffects)

            # Set reciprocal edge as a reciprocal
            self.setTransitionReciprocal(fromDecision, transition, revName)

        # Merge extra double-reciprocal properties if we found any
        if extraRevRevProps is not None:
            tProps = mergeProperties(tProps, extraRevRevProps)

        # Apply old transition properties
        self.setTransitionProperties(fromDecision, transition, **tProps)

        # Remove 'unknown' tag
        try:
            self.untagTransition(fromDecision, transition, 'unknown')
        except KeyError:
            pass

        # Accumulate new tags & annotations
        self.tagTransition(fromDecision, transition, tags)
        self.annotateTransition(fromDecision, transition, annotations)

        # Override copied requirement/effects
        if requirement is not None:
            self.setTransitionRequirement(
                fromDecision,
                transition,
                requirement
            )
        if applyEffects is not None:
            self.setTransitionEffects(
                fromDecision,
                transition,
                applyEffects
            )

    def addEnding(
        self,
        fromDecision: Decision,
        name: Decision,
        tags: Optional[Set[Tag]] = None,
        annotations: Optional[List[Annotation]] = None,
        endTags: Optional[Set[Tag]] = None,
        endAnnotations: Optional[List[Annotation]] = None,
        requires: Union[Requirement, str, None] = None,
        effects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds an edge labeled `'_e:-name-'` where '-name-' is the provided
        name, connecting to a new (or existing) decision named
        `'_e:-name-'` (same as the edge). This represents a transition to
        a game-end state. No reciprocal edge is added, but tags may be
        applied to the added transition and/or the ending room. The new
        transition and decision are both automatically tagged with
        'ending'.

        The starting decision must already exist, and must not already
        have a transition with the transition name, or a `ValueError`
        will be raised. Note that this means that ending names should not
        overlap with common transition names, since they may need to be
        used from multiple decisions in the graph; the '_e:' prefix
        should help with this.

        Requirements and/or effects if provided will be applied to the
        transition.
        """
        # Defaults
        if tags is None:
            tags = set()
        if annotations is None:
            annotations = []
        if endTags is None:
            endTags = set()
        if endAnnotations is None:
            endAnnotations = []

        tags.add("ending")
        endTags.add("ending")

        namePlus = '_e:' + name

        # Error checking
        if fromDecision not in self:
            raise ValueError(
                f"Cannot add a new ending transition '{name}' to"
                f" '{fromDecision}': That decision does not exist."
            )

        if namePlus in self.destinationsFrom(fromDecision):
            raise ValueError(
                f"Cannot add a new ending edge '{name}':"
                f" '{fromDecision}' already has an outgoing edge named"
                f" '{namePlus}'."
            )

        # Create or new ending decision if we need to
        if namePlus not in self:
            self.add_node(namePlus, tags=endTags, ann=endAnnotations)
        else:
            # Or tag/annotate the existing decision
            self.tagDecision(namePlus, endTags)
            self.annotateDecision(namePlus, endAnnotations)

        # Add the edge
        self.add_edge(
            fromDecision,
            namePlus,
            key=namePlus,
            tags=tags,
            ann=annotations
        )
        self.setTransitionRequirement(fromDecision, namePlus, requires)
        if effects is not None:
            self.setTransitionEffects(fromDecision, namePlus, effects)


class TransitionBlockedWarning(Warning):
    """
    An warning type for indicating that a transition which has been
    requested does not have its requirements satisfied by the current
    game state.
    """
    pass


class Exploration:
    """
    A list of `DecisionGraph`s representing exploration over time, with
    specific positions for each step and transitions into them
    specified. Each decision graph represents a new state of the world
    (and/or new knowledge about a persisting state of the world), and the
    transition between graphs indicates which edge was followed, or what
    event happened to cause update(s). Depending on the resolution, it
    could represent a close record of every decision made or a more
    coarse set of snapshots from gameplay with more time in between.
    """
    def __init__(self) -> None:
        self.graphs: List[DecisionGraph] = []
        self.positions: List[Decision] = []
        self.states: List[State] = []
        self.transitions: List[Transition] = []
        # The transition at index i indicates the transition followed
        # (from the decision in the positions list at index i) or the
        # action taken that leads to the graph and position at index i + 1.
        # Normally, if there are n graphs, there will be n - 1
        # transitions listed.

    def __len__(self) -> int:
        """
        The 'length' of an exploration is the number of steps.
        """
        return len(self.graphs)

    def graphAtStep(self, n: int) -> DecisionGraph:
        """
        Returns the `DecisionGraph` at the given step index. Raises an
        `IndexError` if the step index is out of bounds (see `__len__`).
        """
        return self.graphs[n]

    def getGraphAtStep(self, n: int) -> Optional[DecisionGraph]:
        """
        Like `graphAtStep` but returns None instead of raising an error
        if there is no graph at that step.
        """
        try:
            return self.graphAtStep(n)
        except IndexError:
            return None

    def positionAtStep(self, n: int) -> Decision:
        """
        Returns the position at the given step index. Raises an `IndexError`
        if the step index is out of bounds (see `__len__`).
        """
        return self.positions[n]

    def getPositionAtStep(self, n: int) -> Optional[Decision]:
        """
        Like `positionAtStep` but returns None instead of raising
        an error if there is no position at that step.
        """
        try:
            return self.positionAtStep(n)
        except IndexError:
            return None

    def stateAtStep(self, n: int) -> State:
        """
        Returns the game state at the specified step. Raises an
        `IndexError` if the step value is out-of-bounds.
        """
        return self.states[n]

    def getStateAtStep(self, n: int) -> Optional[State]:
        """
        Like `stateAtStep` but returns None instead of raising
        an error if there is no transition at that step.
        """
        try:
            return self.stateAtStep(n)
        except IndexError:
            return None

    def transitionAtStep(self, n: int) -> Optional[Transition]:
        """
        Returns the transition taken from the situation at the given step
        index to the next situation (a `Transition` indicating which exit
        or action was taken). Raises an `IndexError` if the step index is
        out of bounds (see `__len__`), but returns `None` for the last
        step, which will not have a transition yet.
        """
        # Negative indices need an offset
        if n < 0:
            if n == -1 and len(self.graphs) > 0:
                transition = None
            else:
                transition = self.transitions[n + 1]
        # Positive indices just allow for None if we go one over
        else:
            if n == len(self.transitions) and len(self.graphs) > 0:
                transition = None
            else:
                # IndexError here for inappropriate indices
                transition = self.transitions[n]

        return transition

    def getTransitionAtStep(
        self,
        n: int
    ) -> Optional[Transition]:
        """
        Like `transitionAtStep` but returns None instead of raising
        an error if there is no transition at that step.
        """
        try:
            return self.transitionAtStep(n)
        except IndexError:
            return None

    def situationAtStep(
        self,
        n: int
    ) -> Tuple[DecisionGraph, Decision, State, Optional[Transition]]:
        """
        Returns a 4-tuple containing the graph (a `DecisionGraph`), the
        position (a `Decision`), the state (a `State`), and the
        transition taken (either a `Transition` or None) at the
        specified step. For the last step, the transition will be None.
        Raises an `IndexError` if asked for a step that's out-of-range.
        """

        return (
            self.graphs[n],
            self.positions[n],
            self.states[n],
            self.transitionAtStep(n)
        )

    def getSituationAtStep(
        self,
        n: int
    ) -> Optional[
        Tuple[DecisionGraph, Decision, State, Optional[Transition]]
    ]:
        """
        Like `situationAtStep` but returns None instead of raising an
        error if there is no situation at that step.
        """
        try:
            return self.situationAtStep(n)
        except IndexError:
            return None

    def currentGraph() -> DecisionGraph:
        """
        Returns the current graph, or raises an `IndexError` if there
        are no graphs yet.
        """
        return self.graphAtStep(-1)

    def getCurrentGraph(self) -> Optional[DecisionGraph]:
        "Like `currentGraph`, but returns None if there are no graphs."
        return self.getMapAtStep(-1)

    def currentPosition(self) -> Decision:
        """
        Returns the current position, or raises an `IndexError` if there
        are no positions yet.
        """
        return self.positionAtStep(-1)

    def getCurrentPosition(self) -> Optional[Decision]:
        """
        Like `currentPosition` but returns None if there is no position.
        """
        return self.getPositionAtStep(-1)

    def currentState(self) -> State:
        """
        Returns the current game state, or raises an `IndexError` if
        there are no states yet.
        """
        return self.stateAtStep(-1)

    def getCurrentState(self) -> Optional[State]:
        "Like `getCurrentState` but returns None if there is no state."
        return self.getStateAtStep(-1)

    def currentSituation(
        self
    ) -> Tuple[DecisionGraph, Decision, State, Optional[Transition]]:
        """
        Returns a 4-tuple containing the current graph, the current
        position, the current game state, and None representing the
        current transition, which doesn't exist yet.
        """
        return self.situationAtStep(-1)

    def getCurrentSituation(
        self
    ) -> Optional[
        Tuple[DecisionGraph, Decision, State, Optional[Transition]]
    ]:
        """
        Like `currentSituation` but returns None if there is no current
        situation.
        """
        return self.getSituationAtStep(-1)

    def gainPowerNow(self, power: Power) -> None:
        """
        Modifies the current game state to add the specified `Power` to
        the player's capabilities. No changes are made to the current
        graph.
        """
        self.currentState().setdefault('powers', set()).add(power)

    def losePowerNow(self, power: Power) -> None:
        """
        Modifies the current game state to remove the specified `Power`
        from the player's capabilities. Does nothing if the player
        doesn't already have that power.
        """
        try:
            self.currentState().setdefault('powers', set()).remove(power)
        except KeyError:
            pass

    def adjustTokensNow(self, tokenType: Token, amount: int) -> None:
        """
        Modifies the current game state to add the specified number of
        `Token`s of the given type to the player's tokens. No changes are
        made to the current graph. Reduce the number of tokens by
        supplying a negative amount.
        """
        state = self.currentState()
        tokens = state.setdefault('tokens', {})
        tokens[tokenType] = tokens.get(tokenType, 0) + amount

    def updateRequirementNow(
        self,
        decision: Decision,
        transition: Transition,
        requirement: Union[Requirement, str, None]
    ) -> None:
        """
        Updates the requirement for a specific transition in a specific
        decision. If a `Requirement` object is given, that will be used;
        if a string is given, it will be turned into a `Requirement`
        using `Requirement.parse`. If `None` is given, the requirement
        for that edge will be removed.
        """
        if requirement is None:
            requirement = ReqNothing()
        self.currentMap().setTransitionRequirement(
            decision,
            transition,
            requirement
        )

    def traversableAtStep(
        self,
        step: int,
        decision: Decision,
        transition: Transition
    ) -> bool:
        """
        Returns True if the specified transition from the specified
        decision had its requirement satisfied by the game state at the
        specified step. Raises an `IndexError` if the specified step
        doesn't exist, and a `KeyError` if the decision or transition
        specified does not exist in the `DecisionGraph` at that step.
        """
        graph = self.graphAtStep(step)
        req = graph.getTransitionRequirement(decision, transition)
        return req.satisfied(self.stateAtStep(step))

    def traversableNow(
        self,
        decision: Decision,
        transition: Transition
    ) -> bool:
        """
        Returns True if the specified transition from the specified
        decision has its requirement satisfied by the current game
        state. Raises an `IndexError` if there are no game states yet.
        """
        return self.traversableAtStep(-1, decision, transition)

    def applyEffectsNow(
        self,
        effects: TransitionEffects
    ) -> None:
        """
        Applies the specified effects to the current graph, without
        creating a new exploration step.

        A `ValueError` will be raised if one of the specified tag changes
        doesn't start with either '+' or '-'. Removal of non-applied
        tags is silently ignored however, as is the loss of non-possessed
        powers.
        """
        now = self.currentMap()

        for gain in effects.get('gain', set()):
            if isinstance(gain, str):
                self.gainPowerNow(gain)
            else:
                tokens, amount = gain
                self.adjustTokensNow(tokens, amount)

        for lose in effects.get('lose', set()):
            if isinstance(lose, str):
                self.losePowerNow(lose)
            else:
                tokens, amount = lose
                self.adjustTokensNow(tokens, -amount)

        for decision, transition, req in effects.get('alters', []):
            now.setTransitionRequirement(decision, transition, req)

        for entry in effects.get('tags', []):
            if len(entry) == 2:
                entry = cast(Tuple[Decision, List[Tag]], entry)
                tagDecision, taglist = entry
                for tagChange in taglist:
                    action = tagChange[0]
                    theTag = tagChange[1:]
                    if action == '+':
                        now.tagDecision(tagDecision, theTag)
                    elif action == '-':
                        try:
                            now.untagDecision(tagDecision, theTag)
                        except KeyError:
                            pass
                    else:
                        raise ValueError(
                            f"Invalid taglist entry '{tagChange}'"
                            f" (didn't start with either '+' or '-')."
                        )
            else: # length must be 3
                entry = cast(Tuple[Decision, Transition, List[Tag]], entry)
                decision, transition, taglist = entry
                for tagChange in taglist:
                    action = tagChange[0]
                    theTag = tagChange[1:]
                    if action == '+':
                        now.tagTransition(decision, transition, theTag)
                    elif action == '-':
                        try:
                            now.untagTransition(decision, transition, theTag)
                        except KeyError:
                            pass
                    else:
                        raise ValueError(
                            f"Invalid taglist entry '{tagChange}'"
                            f" (didn't start with either '+' or '-')."
                        )

    def applyTransitionEffectsNow(
        self,
        decision: Decision,
        transition: Transition,
        step: int = -1
    ) -> None:
        """
        Applies the effects of the specified transition from the
        specified decision to the current graph and state. By default,
        these effects are read from the transition information in the
        current graph, but specifying a non-default `step` value will
        cause the effects to be read from the graph at a different step.
        The effects in the current graph will be updated based on the
        `'next'` entry of the effects object applied.

        Raises an `IndexError` if the specified step doesn't exist, or a
        `KeyError` if the decision or transition specified doesn't exist
        in the graph at the specified step.

        This function does not check whether any requirements for the
        specified transition are satisfied.
        """
        then = self.graphAtStep(step)
        effects = then.getTransitionEffects(decision, transition)
        self.applyEffectsNow(effects)

    def start(
        self,
        decisionName: Decision,
        connectionNames: Iterable[Transition],
        startState: Dict[str, Any] = None
    ) -> None:
        """
        Creates a new initial graph, and places one decision in that
        graph with the given name and with connections to unknown nodes
        for each of the connection names provided. These connections are
        set up without any properties or effects.

        Raises a `ValueError` if the exploration isn't empty.
        """
        if len(self.graphs) > 0:
            raise ValueError(
                "Cannot start an exploration which already has graphs in"
                " it."
            )

        if startState is None:
            startState = {}

        first = DecisionGraph()
        first.addDecision(decisionName)
        for connection in connectionNames:
            first.addUnexploredEdge(decisionName, connection)

        # Add the graph to our graphs list and set our starting position
        self.graphs.append(first)
        self.positions.append(decisionName)
        self.states.append(startState)

        # Transitions remains empty for now

    def explore(
        self,
        transition: Transition,
        destination: Decision,
        connectionNames: Iterable[Transition],
        reciprocal: Optional[Transition]
    ) -> None:
        """
        Adds a new graph to the exploration graph representing the
        traversal of the specified transition from the current position,
        and updates the current position to be the new decision added.
        The transition must have been pointing to an unexplored region,
        which will be replaced by a new decision with the given name.
        That decision will have each of the given connections added to
        it (pointing to new unexplored regions), and a reciprocal
        connection back to the old position will be added unless
        `reciprocal` is set to None explicitly.

        An `IndexError` will be raised if there aren't any existing
        graphs, and a `KeyError` will be raised if the current position
        is invalid or if the listed transition does not exist at the
        current position. A `ValueError` will be raised if the specified
        transition does not lead to an unknown region, or if the
        specified destination already exists, and a
        `TransitionBlockedWarning` will be issued if the specified
        transition is not traversable given the current game state (but
        in that last case the step will still be taken).

        The reciprocal may not be one of the listed new connections to
        create (because they will all be created pointing to unknown
        regions).

        To create a decision with multiple connections back to explored
        space, leave those connections out of the `connectionNames`
        argument, and add them manually afterwards by modifying the
        result of `currentMap`.
        """
        here = self.currentPosition()
        if not self.traversableNow(here, transition):
            warnings.warn(
                (
                    f"The requirements for transition '{transition}'"
                    f" from decision '{here}' are not met at step"
                    f" {len(self)}."
                ),
                TransitionBlockedWarning
            )

        now = copy.deepcopy(self.currentMap())
        current = copy.deepcopy(self.currentState())

        if destination in now:
            raise ValueError(
                f"Cannot explore to decision '{destination}' because it"
                f" already exists (use `returnTo` when revisiting a"
                f" previous decision)."
            )

        now.replaceUnexplored(
            here,
            transition,
            destination,
            reciprocal
        )

        for outgoing in connectionNames:
            now.addUnexploredEdge(destination, outgoing)

        # Grow our state-list variables
        self.graphs.append(now)
        self.transitions.append(transition)
        self.positions.append(destination)
        self.states.append(current)

        # Pick up state effects of the transition
        self.applyTransitionEffectsNow(here, transition)
        # Note: we apply the transition effects from the copied + updated
        # graph, not from the previous-step graph. This shouldn't make
        # any difference, since we just copied the graph.

    def returnTo(
        self,
        transition: Transition,
        destination: Decision,
        reciprocal: Optional[Transition] = None
    ) -> None:
        """
        Adds a new graph to the exploration that replaces the given
        transition at the current position (which must lead to an unknown
        node, or a `ValueError` will result). The new transition will
        connect back to the specified destination, which must already
        exist (or a different `ValueError` will be raised).

        If a `reciprocal` transition is specified, that transition must
        either not already exist in the destination decision or lead to
        an unknown region; it will be replaced (or added) as an edge
        leading back to the current position.

        The 'unknown' tag of both the replaced edge and the reciprocal
        edge will be removed if it was present.

        A `TransitionBlockedWarning` will be issued if the requirements
        for the transition are not met, but the step will still be taken.
        """
        # Get current position and graph
        now = copy.deepcopy(self.currentMap())
        here = self.currentPosition()
        state = copy.deepcopy(self.currentState())

        if not self.traversableNow(here, transition):
            warnings.warn(
                (
                    f"The requirements for transition '{transition}'"
                    f" from decision '{here}' are not met at step"
                    f" {len(self)}."
                ),
                TransitionBlockedWarning
            )

        if destination not in now:
            raise ValueError(
                f"Cannot return to decision '{destination}' because it"
                f" does not yet exist (use `explore` when visiting a new"
                f" decision)."
            )

        # Replace with connection to existing destination
        now.replaceUnexplored(
            here,
            transition,
            destination,
            reciprocal
        )

        # Grow our state-list variables
        self.graphs.append(now)
        self.transitions.append(transition)
        self.positions.append(destination)
        self.states.append(state)

        # Apply transition effects
        self.applyTransitionEffectsNow(here, transition)

    def takeAction(
        self,
        action: Transition,
        requires: Union[Requirement, str, None] = None,
        effects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds a new graph to the exploration based on taking the given
        action, which must be a self-transition in the graph. If the
        action does not already exist in the graph, it will be created;
        either way the requirements and effects of the action will be
        updated to match any specified here, and those are the
        requirements/effects that will count. The optional arguments
        specify a requirement and/or effect for the action.

        Issues a `TransitionBlockedWarning` if the current game state
        doesn't satisfy the requirements for the action.
        """
        here = self.currentPosition()
        now = copy.deepcopy(self.currentMap())
        state = copy.deepcopy(self.currentState())
        # If the action doesn't already exist, we create it in the new
        # graph (e.g, if there's a hidden cutscene trigger).
        if now.getDestination(here, action) is None:
            now.addAction(here, action, requires, effects)
        else:
            # Otherwise, just update the transition effects (before the
            # action is taken)
            now.setTransitionRequirement(here, action, requires)
            if effects is not None:
                now.setTransitionEffects(here, action, effects)

        # TODO:

        # Note: can't use traversableNow here, because if we just added
        # the action, it won't appear in the current graph yet
        # (self.graph.append happens below, and must happen after this).
        req = now.getTransitionRequirement(here, action)
        if not req.satisfied(self.currentState()):
            warnings.warn(
                (
                    f"The requirements for action '{action}' in"
                    f" decision '{here}' are not met in the game state"
                    f" at step {len(self)}."
                ),
                TransitionBlockedWarning
            )

        self.graph.append(now)
        self.transitions.append(action)
        self.positions.append(self.currentPosition())
        self.states.append(state)

        self.applyTransitionEffectsNow(here, action)

    def retrace(
        self,
        transition: Transition,
    ) -> None:
        """
        Adds a new graph to the exploration based on taking the given
        transition, which must already exist and which must not lead to
        an unknown region.

        Issues a `TransitionBlockedWarning` if the current game state
        doesn't satisfy the requirements for the transition.

        A `ValueError` is raised if the specified transition does not yet
        exist or leads to an unknown area.
        """
        here = self.currentPosition()
        now = copy.deepcopy(self.currentMap())
        state = copy.deepcopy(self.currentState())
        # If the action doesn't already exist, we create it in the new
        # graph (e.g, if there's a hidden cutscene trigger).
        dest = now.getDestination(here, transition)
        if dest is None:
            raise ValueError(
                f"Cannot retrace transition '{transition}' from"
                f" decision '{here}' because it does not yet exist."
            )

        dest = cast(Decision, dest)

        if 'unknown' in now.transitionTags(here, transition):
            raise ValueError(
                f"Cannot retrace transition '{transition}' from"
                f" decision '{here}' because it leads to an unknown"
                f" decision.\nUse `Exploration.explore` and provide"
                f" destination decision details instead."
            )

        if not self.traversableNow(here, transition):
            warnings.warn(
                (
                    f"The requirements for transition '{transition}' in"
                    f" decision '{here}' are not met in the game state"
                    f" at step {len(self)}."
                ),
                TransitionBlockedWarning
            )

        self.graph.append(now)
        self.transitions.append(transition)
        self.positions.append(dest)
        self.states.append(state)

        self.applyTransitionEffectsNow(here, transition)

    def warp(
        self,
        destination: Decision,
        message: str = "",
        effects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds a new graph to the exploration that's a copy of the current
        graph, listing the transition as '~~:' plus the specified message
        (or just '~~' if the message is an empty string). That transition
        string must NOT be a valid transition in the current room.

        If the destination is the same as the current position, the
        transition prefix (or content) will be '..' instead of '~~'.

        The position is set to the specified destination, and if effects
        are specified they are applied.

        A `ValueError` is raised if the specified transition name
        already exists.

        A `KeyError` is raised if the specified destination does not
        exist.
        """
        here = self.currentPosition()
        now = copy.deepcopy(self.currentMap())
        state = copy.deepcopy(self.currentState())

        if destination not in now:
            raise KeyError(
                f"Warp destination '{destination}' does not exist."
            )

        prefix = '~~'
        if here == destination:
            prefix = '..'

        if message == '':
            tName = prefix
        else:
            tName = prefix + ':' + message

        # If the transition already exists, it's not a valid warp
        # message.
        dest = now.getDestination(here, tName)
        if dest is not None:
            raise ValueError(
                f"Cannot use '{message}' as a warp message because"
                f" transition '{tName}' exists at decision '{here}'."
            )

        self.graph.append(now)
        self.transitions.append(tName)
        self.positions.append(destination)
        self.states.append(state)

        if effects is not None:
            self.applyEffectsNow(effects)

    def wait(
        self,
        message: str = "",
        effects: Optional[TransitionEffects] = None
    ) -> None:
        """
        Adds a warp which leaves the player in the same position. If
        effects are specified, they are applied.

        A `ValueError` is raised if the message implies a transition name
        which already exists (this is unlikely).
        """
        here = self.currentPosition()
        self.warp(here, message, effects)
