"""
- Authors: Peter Mawhorter
- Consulted:
- Date: 2022-3-20
- Purpose: Parsing for journal-format exploration records.

A journal fundamentally consists of a number of records detailing rooms
entered, which entrance was used, which exit was eventually taken, and
what decisions were made in between. Other information like enemies
fought, items acquired, or general comments may also be present. These
records are just part of a string, where blank lines separate records,
and special symbols denote different kinds of entries within a record.

`convertJournal` converts these text journals into `core.Exploration`
objects for a more formal representation of the graph state at each step
of the journal.

To support slightly different journal formats, a `Format` dictionary is
used to define the exact delimiters used for various
events/actions/transitions.
"""

from typing import (
    Optional, List, Tuple, Dict, Union, Literal, Set,
    get_args, cast, Type
)

import re, warnings

from . import core


#----------------------#
# Parse format details #
#----------------------#

JournalEntryType = Literal[
    'room',
    'entrance',
    'exit',
    'blocked',
    'unexplored',
    'unexploredOneway',
    'pickup',
    'unclaimed',
    'randomDrop',
    'progress',
    'frontier',
    'frontierEnd',
    'action',
    'challenge',
    'oops',
    'oneway',
    'hiddenOneway',
    'otherway',
    'detour',
    'unify',
    'obviate',
    'warp',
    'death',
    'runback',
    'traverse',
    'ending',
    'note',
    'tag',
]
"""
One of the types of entries that can be present in a journal. Each
journal line is either an entry or a continuation of a previous entry.
The available types are:

- 'room': Used for room names & detour rooms.
- 'entrance': Indicates an entrance (must come first in a room).
- 'exit': Indicates an exit taken (must be last in a room).
- 'blocked': Indicates a blocked route.
- 'unexplored': Indicates an unexplored exit.
- 'unexploredOneway': Indicates an unexplored exit which is known to be
    one-directional outgoing. Use the 'oneway' or 'hiddenOneway'
    markers instead for in-room one-way transitions, and use 'otherway'
    for one-directional entrances.
- 'pickup': Indicates an item pickup.
- 'unclaimed': Indicates an unclaimed but visible pickup.
- 'randomDrop': Indicates an item picked up via a random drop, which
    isn't necessarily tied to the particular room where it occurred.
    TODO: This!
- 'progress': Indicates progress within a room (engenders a sub-room).
    Also used before the room name in a block to indicate rooms passed
    through while retracing steps. The content is the name of the
    sub-room entered, listing an existing sub-room will create a new
    connection to that sub-room from the current sub-room if necessary.
    This marker can also be used as a sub-room name to refer to the
    default (unnamed) sub-room.
- 'frontier': Indicates a new frontier has opened up, which creates a
    new unknown node tagged 'frontier' to represent that frontier and
    connects it to the current node, as well as creating a new known
    node tagged 'frontier' also connected to the current node. While a
    frontier is open in a certain room, every new sub-room created will
    be connected to both of these nodes. Any requirements or other
    transition properties specified when the frontier is defined will be
    copied to each of the created transitions. If a frontier has been
    closed, it can be re-opened.
- 'frontierEnd': Indicates that a specific frontier is no longer open,
    which removes the frontier's unknown node and prevents further
    sub-rooms from being connected to it. If the frontier is later
    re-opened, a new unknown node will be generated and re-connected to
    each of the sub-rooms previously connected to that frontier;
    transitions to the re-opened unexplored node will copy transition
    properties specified when the frontier is reopened since their old
    transition properties will be lost, and these will also be used for
    new connections to the known frontier node. Old connections to the
    known node of the frontier will not be updated.
- 'action': Indicates an action taken in a room, which does not create a
    sub-room. The effects of the action are not noted in the journal,
    but an accompanying ground-truth map would have them, and later
    journal entries may imply them.
- 'challenge': Indicates a challenge of some sort. A entry tagged with
    'failed' immediately afterwards indicates a challenge outcome.
- 'oops': Indicates mistaken actions in rooms or transitions.
- 'oneway': Indicates a one-way connection inside of a room, which we
    assume is visible as such from both sides. Also used at the end of a
    block for outgoing connections that are visibly one-way.
- 'hiddenOneway': Indicates a one-way connection in a room that's not
    visible as such from the entry side. To mark a hidden one-way
    between rooms, simply use a normal exit marker and a one-way
    entrance marker in the next room.
- 'otherway': Indicates incoming one-ways; also used as an entrance
    marker for the first entry in a block to denote that the entrance
    one just came through cannot be accessed in reverse. Whether this is
    expected or a surprise depends on the exit annotation for the
    preceding block.
- 'detour': Indicates a detour (a quick visit to a one-entrance room
    that doesn't get a full entry), or a quick out-and-in for the current
    room via a particular exit.
- 'unify': Indicates the realization that one's current position is
    actually a previously-known sub-room, with the effect of merging
    those two sub-rooms.
- 'obviate': Indicates when a previously-unexplored between-room transition
    gets explored from the other side, without crossing the transition,
    or when a link back to a known sub-room is observed without actually
    crossing that link.
- 'warp': Indicates a warp not due to a death. Again a particular room
    is named as the destination. Although the player moves, no
    connection is made in the graph, since it's assumed that this is a
    one-time move and/or a repeatable power where the start and/or
    destination are variable. If there's something like a teleporter
    with two fixed endpoints, just use a normal transition. On the other
    hand, if there's a multi-entrance/exit teleporter system,
    represent this using a room for "inside the system" that has
    multiple connections to each of the destinations throughout the
    graph.
- 'death': Indicates a death taken. The content will specify which room
    the player ends up in (usually a save room); depends on the game and
    particular mechanics (like save-anywhere).
- 'runback': Indicates that a detour to the named room was made, after
    which the player returned to the current location in the current room.
    The exact path taken is not specified; it is assumed that nothing of
    note happens along the way (if something did happen, the journal
    should include a room entry and event where it did, so a runback
    would not be used). This is used for things like running back to a
    save point before continuing exploration where you left off.
    TODO: Figure out rules for that path?
    TODO: What about e.g., running somewhere to flip a switch? We could
    allow a single-line anon-room-style action?
- 'traverse': Indicates unspecified traversal through sub-rooms in the
    current room to an existing sub-room.
    TODO: Pathfinding rules for this?
- 'ending': Indicates a game ending state was reached. Progress after
    this implies a save was loaded, and the assumption is hat there is no
    actual link between the rooms before and afterwards. This should only
    appear as the final entry of a journal block (excepting notes/tags).
    If exploration continues in the same room, a new block for that room
    should be made.
- 'note': A comment. May also appear at the end of another entry.
- 'tag': a tag or tags which will be added to the room or transition
    depending on which line they appear on. Tag a room or sub-room by
    putting tag delimiters around space-separated tag words as an entry
    in that room or sub-room, and tag transitions by including tag
    delimiters around tag words at the end of the line defining the
    transition.
"""

JournalInfoType = Literal[
    'subroom',
    'anonSep',
    'unknownItem',
    'tokenQuantity',
    'requirement',
    'reciprocalSeparator',
    'transitionAtDecision'
]
"""
Represents a part of the journal syntax which isn't an entry type but is
used to mark something else. For example, the character denoting a
sub-room as part of a room name. The available values are:

- 'subroom': present in a room name to indicate the rest of the name
    identifies a sub-room. Used to mark some connections as 'internal'
    even when the journal has separate entries.
- 'anonSep': Used to join together a room base name and an exit name to
    form the name of an anonymous room.
- 'unknownItem': Used in place of an item name to indicate that
    although an item is known to exist, it's not yet know what that item
    is. Note that when journaling, you should make up names for items
    you pick up, even if you don't know what they do yet. This notation
    should only be used for items that you haven't picked up because
    they're inaccessible, and despite being apparent, you don't know
    what they are because they come in a container (e.g., you see a
    sealed chest, but you don't know what's in it).
- 'tokenQuantity': This is used to separate a token name from a token
    quantity when defining items picked up. Note that the parsing for
    requirements is not as flexible, and always uses '*' for this, so to
    avoid confusion it's preferable to leave this at '*'.
- 'requirement': used to indicate what is required when something is
    blocked or temporarily one-way, or when traversing a connection that
    would be blocked if not for the current game state.
- 'reciprocalSeparator': Used to indicate, within a requirement or a
    tag set, a separation between requirements/tags to be applied to the
    forward direction and requirements/tags to be applied to the reverse
    direction. Not always applicable (e.g., actions have no reverse
    direction).
- 'transitionAtDecision' Used to separate a decision name from a
    transition name when identifying a specific transition.
"""

JournalMarkerType = Union[JournalEntryType, JournalInfoType]
"Any journal marker type."

DelimiterMarkerType = Literal['room', 'requirement', 'tag']
"""
The marker types which need delimiter marker values.
"""

Format = Dict[JournalMarkerType, str]
"""
A journal format is specified using a dictionary with keys that denote
journal marker types and values which are several-character strings
indicating the markup used for that entry/info type.
"""

DEFAULT_FORMAT: Format = {
    # Room name markers
    'room': '[]',
    # Entrances and exits
    'entrance': '<',
    'exit': '>',
    'oneway': '->',
    'otherway': 'x<', # unexplored when not in entrance position
    # Unexplored options
    'blocked': 'x',
    'unexplored': '?',
    'unexploredOneway': '?>',
    # Special progress
    'detour': '><',
    'unify': '`',
    'obviate': '``',
    'oops': '@',
    # In-room progress (sub-rooms)
    'progress': '-',
    'frontier': '--',
    'frontierEnd': '-/',
    'action': '*',
    'hiddenOneway': '>>',
    # Non-transition events
    'challenge': '#',
    'pickup': '.',
    'unclaimed': ':',
    'randomDrop': '$',
    # Warps and other special transitions
    'warp': '~~',
    'death': '!',
    'runback': '...',
    'traverse': '---',
    'ending': '$$',
    # Annotations
    'note': '"',
    'tag': '{}',
    # Non-entry-type markers
    'subroom': '%',
    'anonSep': '$',
    'unknownItem': '?',
    'tokenQuantity': '*',
    'requirement': '()',
    'reciprocalSeparator': '/',
    'transitionAtDecision': ':',
}
"""
The default `Format` dictionary.
"""


DELIMITERS = {'()', '[]', '{}'}
"""
Marker values which are treated as delimiters.
"""


class ParseFormat:
    """
    A ParseFormat manages the mapping from markers to entry types and
    vice versa.
    """
    def __init__(self, formatDict: Format = DEFAULT_FORMAT):
        """
        Sets up the parsing format. Requires a `Format` dictionary to
        define the specifics. Raises a `ValueError` unless the keys of
        the `Format` dictionary exactly match the `JournalMarkerType`
        values.
        """
        self.formatDict = formatDict

        # Check that formatDict doesn't have any extra keys
        markerTypes = get_args(JournalEntryType) + get_args(JournalInfoType)
        for key in formatDict:
            if key not in markerTypes:
                raise ValueError(
                    f"Format dict has key '{key}' which is not a"
                    f" recognized entry or info type."
                )

        # Check completeness of formatDict
        for mtype in markerTypes:
            if mtype not in formatDict:
                raise ValueError(
                    f"Format dict is missing an entry for marker type"
                    f" '{mtype}'."
                )

        # Check that delimiters are assigned appropriately:
        needDelimeters = get_args(DelimiterMarkerType)
        for needsDelimiter in needDelimeters:
            if formatDict[needsDelimiter] not in DELIMITERS:
                raise ValueError(
                    f"Format dict entry for '{needsDelimiter}' must be"
                    f" a delimiter ('[]', '()', or '{{}}')."
                )

        # Check for misplaced delimiters
        for name in formatDict:
            if (
                name not in needDelimeters
            and formatDict[name] in DELIMITERS
            ):
                raise ValueError(
                    f"Format dict entry for '{name}' may not be a"
                    f" delimiter ('[]', '()', or '{{}}')."
                )

        # Build reverse dictionary from markers to entry types (But
        # exclude info types from this)
        self.entryMap: Dict[str, JournalEntryType] = {}
        entryTypes = set(get_args(JournalEntryType))

        # Inspect each association
        for name, fullMarker in formatDict.items():
            if name not in entryTypes:
                continue

            # Marker is only the first char of a delimiter
            if fullMarker in DELIMITERS:
                marker = fullMarker[0]
            else:
                marker = fullMarker

            # Duplicates not allowed
            if marker in self.entryMap:
                raise ValueError(
                    f"Format dict entry for '{name}' duplicates"
                    f" previous format dict entry for"
                    f" '{self.entryMap[marker]}'."
                )

            # Map markers to entry types
            self.entryMap[marker] = cast(JournalEntryType, name)

        # These are used to avoid recompiling the RE for
        # end-of-anonymous-room markers. See anonymousRoomEnd.
        self.roomEnd = None
        self.anonEndPattern = None

    def markers(self) -> List[str]:
        """
        Returns the list of all entry-type markers (but not info
        markers), sorted from longest to shortest to help avoid
        ambiguities when matching. Note that '()', '[]', and '{}'
        markers are interpreted as delimiters, and should only be used
        for 'room', 'requirement', and/or 'tag' entries.
        """
        return sorted(
            (
                m if m not in DELIMITERS else m[0]
                for (et, m) in self.formatDict.items()
                if et in get_args(JournalEntryType)
            ),
            key=lambda m: -len(m)
        )

    def markerFor(self, markerType: JournalMarkerType) -> str:
        """
        Returns the marker for the specified entry or info type.
        """
        return self.formatDict[markerType]

    def determineEntryType(self, entry: str) -> Tuple[JournalEntryType, str]:
        """
        Given a single line from a journal, returns a tuple containing
        the entry type for that line, and a string containing the entry
        content (which is just the line minus the entry-type-marker).
        """
        bits = entry.strip().split()
        if bits[0] in self.entryMap:
            eType = self.entryMap[bits[0]]
            eContent = entry[len(bits[0]):].lstrip()
        else:
            first = bits[0]
            prefix = None
            # Try from longest to shortest to defeat ambiguity
            for marker in self.markers():
                if first.startswith(marker):
                    prefix = marker
                    eContent = entry[len(marker):]
                    break

            if prefix is None:
                raise JournalParseError(
                    f"Entry does not begin with a recognized entry"
                    f" marker:\n{entry}"
                )
            else:
                eType = self.entryMap[prefix]

        if eType in get_args(DelimiterMarkerType):
            # Punch out the closing delimiter from the middle of the
            # content, since things like requirements or tags might be
            # after it, and the rest of the code doesn't want to have to
            # worry about them (we already removed the starting
            # delimiter).
            marker = self.formatDict[eType]
            matching = eContent.find(marker[-1])
            if matching > -1:
                eContent = eContent[:matching] + eContent[matching + 1:]
            else:
                warnings.warn(
                    (
                        f"Delimiter-style marker '{marker}' is missing"
                        f" closing part in entry:\n{entry}"
                    ),
                    JournalParseWarning
                )

        return eType, eContent

    def parseSpecificTransition(
        self,
        content: str
    ) -> Tuple[core.Decision, core.Transition]:
        """
        Splits a decision:transition pair to the decision and transition
        part, using a custom separator if one is defined.
        """
        sep = self.formatDict['transitionAtDecision']
        n = content.count(sep)
        if n == 0:
            raise JournalParseError(
                f"Cannot split '{content}' into a decision name and a"
                f" transition name (no separator '{sep}' found)."
            )
        elif n > 1:
            raise JournalParseError(
                f"Cannot split '{content}' into a decision name and a"
                f" transition name (too many ({n}) '{sep}' separators"
                f" found)."
            )
        else:
            return cast(
                Tuple[core.Decision, core.Transition],
                tuple(content.split(sep))
            )

    def splitFinalNote(self, content: str) -> Tuple[str, Optional[str]]:
        """
        Given a string defining entry content, splits it into true
        content and another string containing an annotation attached to
        the end of the content. Any text after the 'note' marker on a
        line is part of an annotation, rather than part of normal
        content. If there is no 'note' marker on the line, then the
        second element of the return value will be `None`. Any trailing
        whitespace will be stripped from the content (but not the note).

        A single space will be stripped from the beginning of the note
        if there is one.
        """
        marker = self.formatDict['note']
        if marker in content:
            first = content.index(marker)
            before = content[:first].rstrip()
            after = content[first + 1:]
            if after.startswith(' '):
                after = after[1:]
            return (before, after)
        else:
            return (content.rstrip(), None)

    def splitDelimitedSuffix(
        self,
        content: str,
        delimiters: str,
    ) -> Tuple[str, Optional[str]]:
        """
        Given a string defining entry content, splits it into true
        content and another string containing a part surrounded by the
        specified delimiters (must be a length-2 string). The line must
        end with the ending delimiter (after stripping whitespace) or
        else the second part of the return value will be `None`.

        If the delimiters argument is not a length-2 string or both
        characters are the same, a `ValueError` will be raised. If
        mismatched delimiters are encountered, a `JournalParseError` will
        be raised.

        Whitespace space inside the delimiters will be stripped, as will
        whitespace at the end of the content if a delimited part is found.

        Examples:

        >>> from exploration import journal as j
        >>> pf = j.ParseFormat()
        >>> pf.splitDelimitedSuffix('abc (def)', '()')
        ('abc', 'def')
        >>> pf.splitDelimitedSuffix('abc def', '()')
        ('abc def', None)
        >>> pf.splitDelimitedSuffix('abc [def]', '()')
        ('abc [def]', None)
        >>> pf.splitDelimitedSuffix('abc [d(e)f]', '()')
        ('abc [d(e)f]', None)
        >>> pf.splitDelimitedSuffix(' abc d ( ef )', '()')
        (' abc d', 'ef')
        >>> pf.splitDelimitedSuffix(' abc d ( ef ) ', '[]')
        (' abc d ( ef ) ', None)
        >>> pf.splitDelimitedSuffix(' abc ((def))', '()')
        (' abc', '(def)')
        >>> pf.splitDelimitedSuffix(' (abc)', '()')
        ('', 'abc')
        >>> pf.splitDelimitedSuffix(' a(bc )def)', '()')
        Traceback (most recent call last):
        ...
        exploration.journal.JournalParseError...
        >>> pf.splitDelimitedSuffix(' abc def', 'd')
        Traceback (most recent call last):
        ...
        ValueError...
        >>> pf.splitDelimitedSuffix(' abc .def.', '..')
        Traceback (most recent call last):
        ...
        ValueError...
        """
        if len(delimiters) != 2:
            raise ValueError(
                f"Delimiters must a length-2 string specifying a"
                f" starting and ending delimiter (got"
                f" {repr(delimiters)})."
            )
        begin = delimiters[0]
        end = delimiters[1]
        if begin == end:
            raise ValueError(
                f"Delimiters must be distinct (got {repr(delimiters)})."
            )
        if not content.rstrip().endswith(end) or begin not in content:
            # No requirement present
            return (content, None)
        else:
            # March back cancelling delimiters until we find the
            # matching one
            left = 1
            findIn = content.rstrip()
            for index in range(len(findIn) - 2, -1, -1):
                if findIn[index] == end:
                    left += 1
                elif findIn[index] == begin:
                    left -= 1
                    if left == 0:
                        break

            if left > 0:
                raise JournalParseError(
                    f"Unmatched '{end}' in content:\n{content}"
                )

            return (content[:index].rstrip(), findIn[index + 1:-1].strip())

    def splitDirections(
        self,
        content: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Splits a piece of text using the 'reciprocalSeparator' into two
        pieces. If there is no separator, the second piece will be
        `None`; if either side of the separator is blank, that side will
        be `None`, and if there is more than one separator, a
        `JournalParseError` will be raised. Whitespace will be stripped
        from both sides of each result.

        Examples:

        >>> pf = ParseFormat()
        >>> pf.splitDirections('abc / def')
        ('abc', 'def')
        >>> pf.splitDirections('abc def ')
        ('abc def', None)
        >>> pf.splitDirections('abc def /')
        ('abc def', None)
        >>> pf.splitDirections('/abc def')
        (None, 'abc def')
        >>> pf.splitDirections('a/b/c') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          ...
        JournalParseError: ...
        """
        sep = self.formatDict['reciprocalSeparator']
        count = content.count(sep)
        if count > 1:
            raise JournalParseError(
                f"Too many split points ('{sep}') in content:"
                f" '{content}' (only one is allowed)."
            )

        elif count == 1:
            before, after = content.split(sep)
            before = before.strip()
            after = after.strip()
            return (before or None, after or None)

        else: # no split points
            stripped = content.strip()
            if stripped:
                return stripped, None
            else:
                return None, None

    def splitRequirement(
        self,
        content: str
    ) -> Tuple[str, Optional[core.Requirement], Optional[core.Requirement]]:
        """
        Splits a requirement suffix from main content, returning a
        triple containing the main content and up to two requirements.
        The first requirement is the forward-direction requirement, and
        the second is the reverse-direction requirement. One or both may
        be None to indicate that no requirement in that direction was
        included. Raises a `JournalParseError` if something goes wrong
        with the parsing.
        """
        main, req = self.splitDelimitedSuffix(
            content,
            self.formatDict['requirement']
        )
        print("SPR", main, req)

        # If there wasn't any requirement:
        if req is None:
            return (main, None, None)

        # Split into forward/reverse parts
        fwd, rev = self.splitDirections(req)

        try:
            result = (
                main,
                core.Requirement.parse(fwd) if fwd is not None else None,
                core.Requirement.parse(rev) if rev is not None else None
            )
        except ValueError as e:
            raise JournalParseError(*e.args)

        return result

    def splitTags(self, content: str) -> Tuple[str, Set[str], Set[str]]:
        """
        Works like `splitRequirement` but for tags. The tags are split
        into words and turned into a set, which will be empty if no tags
        are present.
        """
        base, tags = self.splitDelimitedSuffix(
            content,
            self.formatDict['tag']
        )
        if tags is None:
            return (base, set(), set())

        # Split into forward/reverse parts
        fwd, rev = self.splitDirections(tags)

        return (
            base,
            set(fwd.split()) if fwd is not None else set(),
            set(rev.split()) if rev is not None else set()
        )

    def startsAnonymousRoom(self, line: str) -> bool:
        """
        Returns true if the given line from a journal block starts a
        multi-line anonymous room. Use `ParseFormat.anonymousRoomEnd` to
        figure out where the end of the anonymous room is.
        """
        return line.rstrip().endswith(self.formatDict['room'][0])

    def anonymousRoomEnd(self, block, startFrom):
        """
        Given a journal block (a multi-line string) and a starting index
        that's somewhere inside a multi-line anonymous room, returns the
        index within the entire journal block of the end of the room
        (the ending delimiter character). That ending delimiter must
        appear alone on a line.

        Returns None if no ending marker can be found.
        """
        # Recompile our regex only if needed
        if self.formatDict['room'][-1] != self.roomEnd:
            self.roomEnd = self.formatDict['room'][-1]
            self.anonEndPattern = re.compile(rf'^\s*{self.roomEnd}\s*$')

        # Look for our end marker, alone on a line, with or without
        # whitespace on either side:
        nextEnd = self.anonEndPattern.search(block, startFrom)
        if nextEnd is None:
            return None

        # Find the actual ending marker ignoring whitespace that might
        # have been part of the match
        return block.index(self.roomEnd, nextEnd.start())

    def splitAnonymousRoom(
        self,
        content: str
    ) -> Tuple[str, Union[str, None]]:
        """
        Works like `splitRequirement` but for anonymous rooms. If an
        anonymous room is present, the second element of the result will
        be a one-line string containing room content, which in theory
        should be a single event (multiple events would require a
        multi-line room, which is handled by
        `ParseFormat.startsAnonymousRoom` and
        `ParseFormat.anonymousRoomEnd`). If the anonymous room is the
        only thing on the line, it won't be counted, since that's a
        normal room name.
        """
        leftovers, anonRoom = self.splitDelimitedSuffix(
            content,
            self.formatDict['room']
        )
        if not leftovers.strip():
            # Return original content: an anonymous room cannot be the
            # only thing on a line (that's a room label).
            return (content, None)
        else:
            return (leftovers, anonRoom)

    def subRoomName(
        self,
        roomName: core.Decision,
        subName: core.Decision
    ) -> core.Decision:
        """
        Returns a new room name that includes the provided sub-name to
        distinguish it from other parts of the same room. If the subName
        matches the progress marker for this parse format, then just the
        base name is returned.

        Examples:

        >>> fmt = ParseFormat()
        >>> fmt.subRoomName('a', 'b')
        'a%b'
        >>> fmt.subRoomName('a%b', 'c')
        'a%b%c'
        >>> fmt.formatDict['progress'] == '-'
        True
        >>> fmt.subRoomName('a', '-')
        'a'
        """
        if subName == self.formatDict['progress']:
            return roomName
        else:
            return roomName + self.formatDict['subroom'] + subName

    def baseRoomName(self, fullName: core.Decision) -> core.Decision:
        """
        Returns the base room name for a room name that may contain
        one or more sub-room part(s).

        >>> fmt = ParseFormat()
        >>> fmt.baseRoomName('a%b%c')
        'a'
        >>> fmt.baseRoomName('a')
        'a'
        """
        marker = self.formatDict['subroom']
        if marker in fullName:
            return fullName[:fullName.index(marker)]
        else:
            return fullName

    def roomPartName(
        self,
        fullName: core.Decision
    ) -> Optional[core.Decision]:
        """
        Returns the room part name for a room name that may contain
        one or more sub-room part(s). If multiple sub-name parts are
        present, they all included together in one string. Returns None
        if there is no room part name included in the given full name.

        Example:

        >>> fmt = ParseFormat()
        >>> fmt.roomPartName('a%b')
        'b'
        >>> fmt.roomPartName('a%b%c')
        'b%c'
        >>> fmt.roomPartName('a%')
        ''
        >>> fmt.roomPartName('a')
        None
        """
        marker = self.formatDict['subroom']
        if marker in fullName:
            return fullName[fullName.index(marker) + 1:]
        else:
            return None

    def roomMinusPart(
        self,
        fullName: core.Decision,
        partName: core.Decision
    ) -> core.Decision:
        """
        Returns the room name, minus the specified sub-room indicator.
        Raises a `JournalParseError` if the full room name does not end
        in the given sub-room indicator.
        Examples:

        >>> fmt = ParseFormat()
        >>> fmt.roomMinusPart('a%b', 'b')
        'a'
        >>> fmt.roomMinusPart('a%b%c', 'c')
        'a%b'
        >>> fmt.roomMinusPart('a%b%c', 'b') # doctest: +IGNORE_EXCEPTION_DETAIL
        Traceback (most recent call last):
          ...
        JournalParseError: ...
        """
        marker = self.formatDict['subroom']
        if not fullName.endswith(marker + partName):
            raise JournalParseError(
                f"Cannot remove sub-room part '{partName}' from room"
                f" '{fullName}' because it does not end with that part."
            )

        return fullName[:-(len(partName) + 1)]

    def allSubRooms(
        self,
        graph: core.DecisionGraph,
        roomName: core.Decision
    ) -> Set[core.Decision]:
        """
        The journal format organizes decisions into groups called
        "rooms" within which "sub-rooms" indicate specific parts where a
        decision is needed. This function returns a set of
        `core.Decision`s naming each decision that's part of the named
        room in the given graph. If the name contains a sub-room part,
        that part is ignored. The parse format is used to understand how
        sub-rooms are named. Note that unknown nodes will NOT be
        included, even if the connections to them are tagged with
        'internal', which is used to tag within-room transitions.

        Note that this function requires checking each room in the entire
        graph, since there could be disconnected components of a room.
        """
        base = self.baseRoomName(roomName)
        return {
            node
            for node in graph.nodes
            if self.baseRoomName(node) == base
            and not graph.isUnknown(node)
        }

    def getEntranceDestination(
        self,
        graph: core.DecisionGraph,
        room: core.Decision,
        entrance: core.Transition
    ) -> Optional[core.Decision]:
        """
        Given a graph and a room being entered, as well as the entrance
        name in that room (i.e., the name of the reciprocal of the
        transition being used to enter the room), returns the name of
        the specific sub-room being entered, based on the known site for
        that entrance, or returns None if that entrance hasn't been used
        in any sub-room of the specified room. If the room has a
        sub-room part in it, that will be ignored.

        Before searching the entire graph, we do check whether the given
        transition exists in the target (possibly sub-) room.
        """
        easy = graph.getDestination(room, entrance)
        if easy is not None:
            return cast(core.Decision, easy)

        check = self.allSubRooms(graph, room)
        for sub in check:
            hope = graph.getDestination(sub, entrance)
            if hope is not None:
                return cast(core.Decision, hope)

        return None

    def getSubRoom(
        self,
        graph: core.DecisionGraph,
        roomName: core.Decision,
        subPart: core.Decision
    ) -> Optional[core.Decision]:
        """
        Given a graph and a room name, plus a sub-room name, returns the
        name of the existing sub-room that's part of the same room as
        the target room but has the specified sub-room name part.
        Returns None if no such room has been defined already.
        """
        base = self.baseRoomName(roomName)
        lookingFor = self.subRoomName(base, subPart)
        if lookingFor in graph:
            return lookingFor
        else:
            return None

    def parseItem(
        self,
        item: str
    ) -> Union[core.Power, Tuple[core.Token, int]]:
        """
        Parses an item, which is either a power (just a string) or a
        token-type:number pair (returned as a tuple with the number
        converted to an integer). The 'tokenQuantity' format value
        determines the separator which indicates a token instead of a
        power.
        """
        sep = self.formatDict['tokenQuantity']
        if sep in item:
            # It's a token w/ an associated count
            parts = item.split(sep)
            if len(parts) != 2:
                raise JournalParseError(
                    f"Item '{item}' has a '{sep}' but doesn't separate"
                    f" into a token type and a count."
                )
            typ, count = parts
            try:
                num = int(count)
            except ValueError:
                raise JournalParseError(
                    f"Item '{item}' has invalid token count '{count}'."
                )

            return (typ, num)
        else:
            # It's just a power
            return item

    def anonName(self, room: core.Decision, exit: core.Transition):
        """
        Returns the anonymous room name for an anonymous room that's
        connected to the specified room via the specified transition.
        Example:

        >>> pf = ParseFormat()
        >>> pf.anonName('MidHall', 'Bottom')
        'MidHall$Bottom'
        """
        return room + self.formatDict['anonSep'] + exit


#-------------------#
# Errors & Warnings #
#-------------------#

class JournalParseError(ValueError):
    """
    Represents a error encountered when parsing a journal.
    """
    pass


class JournalParseWarning(Warning):
    """
    Represents a warning encountered when parsing a journal.
    """
    pass


class InterRoomEllipsis:
    """
    Represents part of an inter-room path which has been omitted from a
    journal and which should therefore be inferred.
    """
    pass


#-----------------#
# Parsing manager #
#-----------------#

class JournalObserver:
    """
    Keeps track of extra state needed when parsing a journal in order to
    produce a `core.Exploration` object. The methods of this class act
    as an API for constructing explorations that have several special
    properties (for example, some transitions are tagged 'internal' and
    decision names are standardized so that a pattern of "rooms" emerges
    above the decision level). The API is designed to allow journal
    entries (which represent specific observations/events during an
    exploration) to be directly accumulated into an exploration object,
    including some ambiguous entries which cannot be directly
    interpreted until further entries are observed. The basic usage is
    as follows:

    1. Create a `JournalObserver`, optionally specifying a custom
        `ParseFormat`.
    2. Repeatedly either:
        * Call `observe*` API methods corresponding to specific entries
            observed or...
        * Call `JournalObserver.observe` to parse one or more
            journal blocks from a string and call the appropriate
            methods automatically.
    3. Call `JournalObserver.applyState` to clear any remaining
        un-finalized state.
    4. Call `JournalObserver.getExploration` to retrieve the
        `core.Exploration` object that's been created.

    Notes:

    - `JournalObserver.getExploration` may be called at any time to get
        the exploration object constructed so far, and that that object
        (unless it's `None`) will always be the same object (which gets
        modified as entries are observed). Modifying this object
        directly is possible for making changes not available via the
        API, but must be done carefully, as there are important
        conventions around things like decision names that must be
        respected if the API functions need to keep working.
    - To get the latest graph, simply use the
        `core.Exploration.currentGraph` method of the
        `JournalObserver.getExploration` result.
    - If you don't call `JournalObserver.applyState` some entries may
        not have affected the exploration yet, because they're ambiguous
        and further entries need to be observed (or `applyState` needs
        to be called) to resolve that ambiguity.

    ## Example

    >>> obs = JournalObserver()
    >>> obs.getExploration() is None
    True
    >>> # We start by using the observe* methods...
    >>> obs.observeRoom("Start") # no effect until entrance is observed
    >>> obs.getExploration() is None
    True
    >>> obs.observeProgress("bottom") # New sub-room within current room
    >>> e = obs.getExploration()
    >>> len(e) # base state + first movement
    2
    >>> e.positionAtStep(0)
    'Start'
    >>> e.positionAtStep(1)
    'Start%bottom'
    >>> e.transitionAtStep(0)
    'bottom'
    >>> obs.observeOneway("R") # no effect yet (might be one-way progress)
    >>> len(e)
    2
    >>> obs.observeRoom("Second") # Need to know entrance
    >>> len(e) # oneway is now understood to be an inter-room transition
    2
    >>> obs.observeProgress("bad") # Need to see an entrance first!
    Traceback (most recent call last):
    ...
    exploration.journal.JournalParseError...
    >>> obs.observeEntrance("L")
    >>> len(e) # Now full transition can be mapped
    3
    >>> e.positionAtStep(2)
    'Second'
    >>> e.transitionAtStep(1)
    'R'
    >>> e.currentGraph().getTransitionRequirement('Second', 'L')
    ReqImpossible()
    >>> # Now we demonstrate the use of "observe"
    >>> obs.observe("x< T (tall)\n? R\n> B\n\n[Third]\nx< T")
    >>> len(e)
    4
    >>> m2 = e.graphAtStep(2) # Updates were applied without adding a step
    >>> m2.getDestination('Second', 'T')
    '_u:1'
    >>> m2.getTransitionRequirement('Second', 'T')
    ReqPower('tall')
    >>> m2.getDestination('Second', 'R')
    '_u:2'
    >>> m2.getDestination('Second', 'B')
    '_u:3'
    >>> m = e.currentGraph()
    >>> m == e.graphAtStep(3)
    >>> m.getDestination('Second', 'B')
    'Third'
    >>> m.getDestination('Third', 'T')
    'Second'
    >>> m.getTransitionRequirement('Third', 'T') # Due to 'x<' for entrance
    ReqImpossible()
    """
    parseFormat: ParseFormat = ParseFormat()
    """
    The parse format used to parse entries supplied as text. This also
    ends up controlling some of the decision and transition naming
    conventions that are followed, so it is not safe to change it
    mid-journal; it should be set once before observation begins, and
    may be accessed but should not be changed.
    """

    exploration: core.Exploration
    """
    This is the exploration object being built via journal observations.
    Note that the exploration object may be empty (i.e., have length 0)
    even after the first few entries have been observed because in some
    cases entries are ambiguous and are not translated into exploration
    steps until a further entry resolves that ambiguity.
    """

    def __init__(self, parseFormat: Optional[ParseFormat] = None):
        """
        Sets up the observer. If a parse format is supplied, that will
        be used instead of the default parse format, which is just the
        result of creating a `ParseFormat` with default arguments.
        """
        if parseFormat is not None:
            self.parseFormat = parseFormat

        # Create  blank exploration
        self.exploration = core.Exploration()

        # State variables

        # Tracks the current room name and tags for the room, once a
        # room has been declared
        self.currentRoomName: Optional[core.Decision] = None
        self.currentRoomTags: Set[core.Tag] = set()

        # Whether we've seen an entrance/exit yet in the current room
        self.seenRoomEntrance = False

        # The room & transition used to exit
        self.previousRoom = None
        self.previousTransition = None

        # The room & transition identified as our next source/transition
        self.exitTransition = None

        # This tracks the current note text, since notes can continue
        # across multiple lines
        self.currentNote: Optional[Tuple[
            Union[
                core.Decision,
                Tuple[core.Decision, core.Transition]
            ], # target
            bool, # was this note indented?
            str # note text
        ]] = None

        # Tracks a pending progress step, since things like a oneway can
        # be used for either within-room progress OR room-to-room
        # transitions.
        self.pendingProgress: Optional[Tuple[
            core.Transition, # transition name to create
            Union[bool, str], # is it one-way; 'hidden' for a hidden one-way?
            Optional[core.Requirement], # requirement for the transition
            Optional[core.Requirement], # reciprocal requirement
            Optional[Set[core.Tag]], # tags to apply
            Optional[Set[core.Tag]], # reciprocal tags
            Optional[List[core.Annotation]], # annotations to apply
            Optional[List[core.Annotation]] # reciprocal annotations
        ]] = None

        # This tracks the current entries in an inter-room abbreviated
        # path, since we first have to accumulate all of them and then
        # do pathfinding to figure out a concrete inter-room path.
        self.interRoomPath: List[
            Union[Type[InterRoomEllipsis], core.Decision]
        ] = []

        # Tracks presence of an end entry, which must be final in the
        # block it occurs in except for notes or tags.
        self.blockEnded = False


    def observe(self, journalText: str) -> None:
        """
        Ingests one or more journal blocks in text format (as a
        multi-line string) and updates the exploration being built by
        this observer, as well as updating internal state. Note that
        without later calling `applyState`, some parts of the observed
        entries may remain saved as internal state that hasn't yet been
        disambiguated and applied to the exploration (for example, a
        final one-way transition could indicate in-room one-way
        progress, or a one-way transition to another room, and this is
        disambiguated by observing whether the next entry is another
        entry in the same block or a blank line to indicate the end of a
        block.

        This method can be called multiple times to process a longer
        journal incrementally including line-by-line. If you give it an
        empty string, that will count as the end of a journal block (or
        a continuation of space between blocks).

        ## Example:

        >>> obs = JournalObserver()
        >>> obs.observe('''\\
        ... [Room1]
        ... < Top " Comment
        ... x nope (power|tokens*3)
        ... ? unexplored
        ... -> sub_room " This is a one-way transition
        ... -> - " The default sub-room is named '-'
        ... > Bottom
        ...
        ... [Room2]
        ... < Top
        ... * switch " Took an action in this room
        ... ? Left
        ... > Right {blue}
        ...
        ... [Room3]
        ... < Left
        ... # Miniboss " Faced a challenge
        ... . power " Get a power
        ... >< Right [
        ...    - ledge (tall)
        ...    . treasure
        ... ] " Detour to an anonymous room
        ... > Left
        ...
        ... - Room2 " Visited along the way
        ... [Room1]
        ... - nope " Entrance may be omitted if implied
        ... > Right
        ... ''')
        >>> e = obs.getExploration()
        >>> len(e)
        12
        >>> m = e.currentGraph()
        >>> len(m)
        11
        >>> def showDestinations(m, r):
        ...     d = m.destinationsFrom(r)
        ...     for outgoing in d:
        ...         req = m.getTransitionRequirement(r, outgoing)
        ...         if req is None:
        ...             req = ''
        ...         else:
        ...             req = ' (' + repr(req) + ')'
        ...         print(outgoing, d[outgoing] + req)
        ...
        >>> showDestinations(m, "Room1")
        Top _u:0
        nope Room1%nope ReqAny(ReqPower("power"), ReqTokens("tokens", 3))
        unexplored _u:1
        sub_room Room1%sub_room
        sub_room.1 Room1%sub_room ReqImpossible()
        Bottom: Room2
        >>> showDestinations(m, "Room1%nope")
        - Room1 ReqAny(ReqPower("power"), ReqTokens("tokens", 3))
        Right _u:3
        >>> showDestinations(m, "Room1%sub_room")
        - Room1 ReqImpossible()
        -.1 Room1
        >>> showDestinations(m, "Room2")
        Top Room1
        action@5 Room2
        Left _u:2
        Right: Room3
        >>> m.transitionTags("Room3", "Right")
        {'blue'}
        >>> showDestinations(m, "Room3")
        Left Room2
        action@7 Room3
        Right Room3$Right
        >>> showDestinations(m, "Room3$Right")
        ledge Room3$Right%ledge ReqPower("tall")
        return Room3
        >>> showDestinations(m, "Room3$Right%ledge")
        - Room3$Right
        action@9 Room3$Right%ledge
        >>> m.decisionAnnotations("Room3")
        ['challenge: Miniboss']
        >>> e.currentPosition()
        'Room1%nope'

        Note that there are plenty of other annotations not shown in
        this example; see `DEFAULT_FORMAT` for the default mapping from
        journal entry types to markers, and see `JournalEntryType` for
        the explanation for each entry type.

        Most entries start with a marker followed by a single space, and
        everything after that is the content of the entry. A few
        different modifiers are removed from the right-hand side of
        entries first:

        - Notes starting with `"` by default and going to the end of the
            line, possibly continued on other lines that are indented
            and start with the note marker.
        - Tags surrounded by `{` and `}` by default and separated from
            each other by commas and optional spaces. These are applied
            to the current room (if alone on a line) or to the decision
            or transition implicated in the line they're at the end of.
        - Requirements surrounded by `(` and `)` by default, with `/`
            used to separate forward/reverse requirements. These are
            applied to the transition implicated by the rest of the
            line, and are not allowed on lines that don't imply a
            transition. The contents are parsed into a requirement using
            `core.Requirement.parse`. Warnings may be issued for
            requirements specified on transitions that are taken which
            are not met at the time.
        - For detours and a few other select entry types, anonymous room
            or transition info may be surrounded by `[` and `]` at the
            end of the line. For detours, there may be multiple lines
            between `[` and `]` as shown in the example above.
        """
        # Normalize newlines
        journalText = journalText\
            .replace('\r\n', '\n')\
            .replace('\n\r', '\n')\
            .replace('\r', '\n')

        # Line splitting variables
        lineNumber = 0 # first iteration will increment to 1 before use
        cursor = 0 # Character index into the block tracking progress
        journalLen = len(journalText) # So we know when to stop
        lineIncrement = 1 # How many lines we've processed
        thisBlock = '' # Lines in this block of the journal

        # Shortcut variable
        pf = self.parseFormat

        # Parse each line separately, but collect multiple lines for
        # multi-line entries such as detours
        while cursor < journalLen:
            lineNumber += lineIncrement
            lineIncrement = 1
            try:
                # Find the next newline
                nextNL = journalBlock.index('\n', cursor)
                fullLine = journalBlock[cursor:nextNL]
                cursor = nextNL + 1
            except ValueError:
                # If there isn't one, rest of the journal is the next line
                fullLine = journalBlock[cursor:]
                cursor = journalLen

            thisBlock += fullLine + '\n'

            # TODO: DEBUG
            print("LL", lineNumber, fullLine)

            # Check for and split off anonymous room content
            line, anonymousContent = pf.splitAnonymousRoom(fullLine)
            if (
                anonymousContent is None
            and pf.startsAnonymousRoom(fullLine)
            ):
                endIndex = pf.anonymousRoomEnd(journalText, cursor)
                if endIndex is None:
                    raise JournalParseError(
                        f"Anonymous room started on line {lineNumber}"
                        f" was never closed in block:\n{thisBlock}\n..."
                    )
                anonymousContent = journalBlock[nextNL + 1:endIndex].strip()
                thisBlock += anonymousContent + '\n'
                # TODO: Is this correct?
                lineIncrement = anonymousContent.count('\n') + 1
                # Skip to end of line where anonymous room ends
                cursor = journalText.index('\n', endIndex + 1)

                # Trim the start of the anonymous room from the line end
                line = line.rstrip()[:-1]

            # Blank lines end one block and start another
            if not line.strip():
                thisBlock = ''
                lineNumber = 0
                self.previousRoom = self.exploration.currentPosition()
                self.previousTransition = self.exitTransition
                self.exitTransition = None
                self.currentRoomName = None
                self.blockEnded = False
                # TODO: More inter-block state here...!
                continue

            # Check for indentation (mostly ignored, but important for
            # comments).
            indented = line[0] == ' '

            # Strip indentation going forward
            line = line.strip()

            # Detect entry type and separate content
            eType, eContent = pf.determineEntryType(line)

            # TODO: DEBUG
            print("EE", lineNumber, eType, eContent)

            if self.exitTransition is not None and eType != 'note':
                raise JournalParseError(
                    f"Entry after room exit on line {lineNumber} in"
                    f" block:\n{thisBlock}"
                )

            if (
                eType not in ('detour', 'obviate')
            and anonymousContent is not None
            ):
                raise JournalParseError(
                    f"Entry on line #{lineNumber} with type {eType}"
                    f" does not support anonymous room content. Block"
                    f" is:\n{thisBlock}"
                )

            # Handle note creation
            if self.currentNote is not None and eType != 'note':
                # This ends a note, so we can apply the pending note and
                # reset it.
                self.applyCurrentNote()
            elif eType == 'note':
                self.observeNote(eContent, indented=indented)
                # In (only) this case, we've handled the entire line
                continue

            # Handle a pending progress step if there is one
            if self.pendingProgress is not None:
                # Any kind of entry except a note (which we would have
                # hit above and continued) indicates that a progress
                # marker is in-room progress rather than being a room
                # exit.
                self.makeProgressInRoom(*pendingProgress)

                # Clean out pendingProgress
                self.pendingProgress = None

            # Check for valid eType if pre-room
            if (
                self.currentRoomName is None
            and eType not in ('room', 'progress')
            ):
                raise JournalParseError(
                    f"Invalid entry on line #{lineNumber}: Entry type"
                    f" '{eType}' not allowed before room name. Block"
                    f" is:\n{thisBlock}"
                )

            # Check for valid eType if post-room
            if self.blockEnded and eType not in ('note', 'tag'):
                raise JournalParseError(
                    f"Invalid entry on line #{lineNumber}: Entry type"
                    f" '{eType}' not allowed after an block ends. Block"
                    f" is:\n{thisBlock}"
                )

            # Parse a line-end note if there is one
            # Note that note content will be handled after we handle main
            # entry stuff
            content, note = pf.splitFinalNote(eContent)

            # Parse a line-end tags section if there is one
            content, fTags, rTags = pf.splitTags(content)

            # Parse a line-end requirements section if there is one
            content, forwardReq, backReq = pf.splitRequirement(content)

            # Strip any remaining whitespace from the edges of our content
            content = content.strip()

            # Get current graph
            now = self.exploration.getCurrentGraph()

            # This will trigger on the first line in the room, and handles
            # the actual room creation in the graph
            handledEntry = False # did we handle the entry in this block?
            if (
                self.currentRoomName is not None
            and not self.seenRoomEntrance
            ):
                # We're looking for an entrance and if we see anything else
                # except a tag, we'll assume that the entrance is implicit,
                # and give an error if we don't have an implicit entrance
                # set up. If the entrance is explicit, we'll give a warning
                # if it doesn't match the previous entrance for the same
                # prior-room exit from last time.
                if eType in ('entrance', 'otherway'):
                    # An explicit entrance; must match previous associated
                    # entrance if there was one.
                    self.observeRoomEntrance(
                        content,
                        etype == 'otherway',
                        fReq = forwardReq,
                        rReq = backReq,
                        fTags = fTags,
                        rTags = rTags
                    )

                    # An otherway marker can be used as an entrance to
                    # indicate that the connection is one-way. Note that for
                    # a one-way connection, we may have a requirement
                    # specifying that the reverse connection exists but
                    # can't be traversed yet. In cases where there is no
                    # requirement, we *still* add a reciprocal edge to the
                    # graph, but mark it as `ReqImpossible`. This is because
                    # we want the rooms' adjacency to be visible from both
                    # sides, and some of our graph algorithms have to respect
                    # requirements anyways. Cases where a reciprocal edge
                    # will be absent are one-way teleporters where there's
                    # actually no sealed connection indicator in the
                    # destination room. TODO: Syntax for those?

                    # Get transition name
                    transitionName = content

                    # If this is not the start of the exploration or a
                    # reset after an ending, check for a previous transition
                    # entering this decision from the same previous
                    # room/transition.
                    prevReciprocal = None
                    prevDestination = None
                    if enterFrom is not None and now is not None:
                        fromDecision, fromTransition = enterFrom
                        prevReciprocal = now.transitionReciprocal(
                            fromDecision,
                            fromTransition
                        )
                        prevDestination = cast(
                            core.Decision,
                            now.getDestination(
                                fromDecision,
                                fromTransition
                            )
                        )
                        if prevDestination is None:
                            raise JournalParseError(
                                f"Transition {fromTransition} from"
                                f" {fromDecision} was named as exploration"
                                f" point but has not been created!"
                            )

                        # If there is a previous reciprocal edge marked, and
                        # it doesn't match the entering reciprocal edge,
                        # that's an inconsistency, unless that edge was
                        # coming from an unknown node.
                        if (
                            not now.isUnknown(prevDestination)
                        and prevReciprocal != transitionName
                        ): # prevReciprocal of None won't be
                            warnings.warn(
                                (
                                    f"Explicit incoming transition from"
                                    f" {fromDecision}:{fromTransition}"
                                    f" entering {roomName} via"
                                    f" {transitionName} does not match"
                                    f" previous entrance point for that"
                                    f" transition, which was"
                                    f" {prevReciprocal}. The reciprocal edge"
                                    f" will NOT be updated."
                                ),
                                JournalParseWarning
                            )

                        # Similarly, if there is an outgoing transition in
                        # the destination room whose name matches the
                        # declared reciprocal but whose destination isn't
                        # unknown and isn't he current location, that's an
                        # inconsistency
                        prevRevDestination = now.getDestination(
                            roomName,
                            transitionName
                        )
                        if (
                            prevRevDestination is not None
                        and not now.isUnknown(
                                cast(core.Decision, prevRevDestination)
                            )
                        and prevRevDestination != fromDecision
                        ):
                            warnings.warn(
                                (
                                    f"Explicit incoming transition from"
                                    f" {fromDecision}:{fromTransition}"
                                    f" entering {roomName} via"
                                    f" {transitionName} does not match"
                                    f" previous destination for"
                                    f" {transitionName} in that room, which was"
                                    f" {prevRevDestination}. The reciprocal edge"
                                    f" will NOT be updated."
                                    # TODO: What will happen?
                                ),
                                JournalParseWarning
                            )

                    seenEntrance = True
                    handledEntry = True
                    if enterFrom is None or now is None:
                        # No incoming transition info
                        if len(exploration) == 0:
                            # Start of the exploration
                            exploration.start(roomName, [])
                            # with an explicit entrance.
                            exploration.currentGraph().addUnexploredEdge(
                                roomName,
                                transitionName,
                                tags=fTags,
                                revTags=rTags,
                                requires=forwardReq,
                                revRequires=backReq
                            )
                        else:
                            # Continuing after an ending MUST NOT involve an
                            # explicit entrance, because the transition is a
                            # warp. To annotate a warp where the character
                            # enters back into the game using a traversable
                            # transition (and e.g., transition effects
                            # apply), include a block noting their presence
                            # on the other side of that doorway followed by
                            # an explicit transition into the room where
                            # control is available, with a 'forced' tag. If
                            # the other side is unknown, just use an
                            # unexplored entry as the first entry in the
                            # block after the ending.
                            raise JournalParseError(
                                f"On line #{lineNumber}, an explicit"
                                f" entrance is not allowed because the"
                                f" previous block ended with an ending."
                                f" Block is:\n{journalBlock}"
                            )
                    else:
                        # Implicitly, prevDestination must not be None here,
                        # since a JournalParseError would have been raised
                        # if enterFrom was not None and we didn't get a
                        # prevDestination. But it might be an unknown area.
                        prevDestination = cast(core.Decision, prevDestination)

                        # Extract room & transition we're entering from
                        fromRoom, fromTransition = enterFrom

                        # If we've seen this room before, check for an old
                        # transition destination, since we might implicitly
                        # be entering a sub-room.
                        if now is not None and roomName in now:
                            if now.isUnknown(prevDestination):
                                # The room already exists, but the
                                # transition we're taking to enter it is not
                                # one we've used before. If the entry point
                                # is not a known transition, unless the
                                # journaler has explicitly tagged the
                                # reciprocal transition with 'discovered', we
                                # assume entrance is to a new sub-room, since
                                # otherwise the transition should have been
                                # known ahead of time.
                                # TODO: Does this mean we have to search for
                                # matching names in other sub-room parts
                                # when doing in-room transitions... ?
                                exploration.returnTo(
                                    fromTransition,
                                    roomName,
                                    transitionName
                                )
                            else:
                                # We already know where this transition
                                # leads
                                exploration.retrace(fromTransition)
                        else:
                            # We're entering this room for the first time.
                            exploration.explore(
                                fromTransition,
                                roomName,
                                [],
                                transitionName
                            )
                        # Apply forward tags to the outgoing transition
                        # that's named, and reverse tags to the incoming
                        # transition we just followed
                        now = exploration.currentGraph() # graph was updated
                        here = exploration.currentPosition()
                        now.tagTransition(here, transitionName, fTags)
                        now.tagTransition(fromRoom, fromTransition, rTags)

                elif eType == 'tag':
                    roomTags |= set(content.split())
                    if fTags or rTags:
                        raise JournalParseError(
                            f"Found tags on tag entry on line #{lineNumber}"
                            f" of block:\n{journalBlock}"
                        )
                    # don't do anything else here since it's a tag;
                    # seenEntrance remains False
                    handledEntry = True

                else:
                    # For any other entry type, it counts as an implicit
                    # entrance. We need to follow that transition, or if an
                    # appropriate link does not already exist, raise an
                    # error.
                    seenEntrance = True
                    # handledEntry remains False in this case

                    # Check that the entry point for this room can be
                    # deduced, and deduce it so that we can figure out which
                    # sub-room we're actually entering...
                    if enterFrom is None:
                        if len(exploration) == 0:
                            # At the start of the exploration, there's often
                            # no specific transition we come from, which is
                            # fine.
                            exploration.start(roomName, [])
                        else:
                            # Continuation after an ending
                            exploration.warp(roomName, 'restart')
                    else:
                        fromDecision, fromTransition = enterFrom
                        prevReciprocal = None
                        if now is not None:
                            prevReciprocal = now.transitionReciprocal(
                                fromDecision,
                                fromTransition
                            )
                        if prevReciprocal is None:
                            raise JournalParseError(
                                f"Implicit transition into room {roomName}"
                                f" is invalid because no reciprocal"
                                f" transition has been established for exit"
                                f" {fromTransition} in previous room"
                                f" {fromDecision}."
                            )

                        # In this case, we retrace the transition, and if
                        # that fails because of a ValueError (e.g., because
                        # that transition doesn't exist yet or leads to an
                        # unknown node) then we'll raise the error as a
                        # JournalParseError.
                        try:
                            exploration.retrace(fromTransition)
                        except ValueError as e:
                            raise JournalParseError(
                                f"Implicit transition into room {roomName}"
                                f" is invalid because:\n{e.args[0]}"
                            )

                        # Note: no tags get applied here, because this is an
                        # implicit transition, so there's no room to apply
                        # new tags. An explicit transition could be used
                        # instead to update transition properties.

            # Previous block may have updated the current graph
            now = exploration.getCurrentGraph()

            # At this point, if we've seen an entrance we're in the right
            # room, so we should apply accumulated room tags
            if seenEntrance and roomTags:
                if now is None:
                    raise RuntimeError(
                        "Inconsistency: seenEntrance is True but the current"
                        " graph is None."
                    )

                here = exploration.currentPosition()
                now.tagDecision(here, roomTags)
                roomTags = set() # reset room tags

            # Handle all entry types not handled above (like note)
            if handledEntry:
                # We skip this if/else but still do end-of-loop cleanup
                pass

            elif eType == 'note':
                raise RuntimeError("Saw 'note' eType in lower handling block.")

            elif eType == 'room':
                if roomName is not None:
                    raise ValueError(
                        f"Multiple room names detected on line {lineNumber}"
                        f" in block:\n{journalBlock}"
                    )

                # Setting the room name changes the loop state
                roomName = content

                # These will be applied later
                roomTags = fTags

                if rTags:
                    raise JournalParseError(
                        f"Reverse tags cannot be applied to a room"
                        f" (found tags {rTags} for room '{roomName}')."
                    )

            elif eType == 'entrance':
                # would be handled above if seenEntrance was false
                raise JournalParseError(
                    f"Multiple entrances on line {lineNumber} in"
                    f" block:\n{journalBlock}"
                )

            elif eType == 'exit':
                # We note the exit transition and will use that as our
                # return value. This also will cause an error on the next
                # iteration if there are further non-note entries in the
                # journal block
                exitRoom = exploration.currentPosition()
                exitTransition = content

                # At this point we add an unexplored edge for this exit,
                # assuming it's not one we've seen before. Note that this
                # does not create a new exploration step (that will happen
                # later).
                knownDestination = None
                if now is not None:
                    knownDestination = now.getDestination(
                        exitRoom,
                        exitTransition
                    )

                    if knownDestination is None:
                        now.addUnexploredEdge(
                            exitRoom,
                            exitTransition,
                            tags=fTags,
                            revTags=rTags,
                            requires=forwardReq,
                            revRequires=backReq
                        )

                    else:
                        # Otherwise just apply any tags to the transition
                        now.tagTransition(exitRoom, exitTransition, fTags)
                        existingReciprocal = now.transitionReciprocal(
                            exitRoom,
                            exitTransition
                        )
                        if existingReciprocal is not None:
                            now.tagTransition(
                                cast(core.Decision, knownDestination),
                                existingReciprocal,
                                rTags
                            )

            elif eType in (
                'blocked',
                'otherway',
                'unexplored',
                'unexploredOneway',
            ):
                # Simply add the listed transition to our current room,
                # leading to an unknown destination, without creating a new
                # exploration step
                transition = content
                here = exploration.currentPosition()

                # If there isn't a listed requirement, infer ReqImpossible
                # where appropriate
                if forwardReq is None and eType in ('blocked', 'otherway'):
                    forwardReq = core.ReqImpossible()
                if backReq is None and eType in ('blocked', 'unexploredOneway'):
                    backReq = core.ReqImpossible()

                # TODO: What if we've annotated a known source for this
                # link?

                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot create an unexplored"
                        f" transition before we've created the starting"
                        f" graph. Block is:\n{journalBlock}"
                    )

                now.addUnexploredEdge(
                    here,
                    transition,
                    tags=fTags,
                    revTags=rTags,
                    requires=forwardReq,
                    revRequires=backReq
                )

            elif eType in ('pickup', 'unclaimed', 'action'):
                # We both add an action to the current room, and then take
                # that action, or if the type is unclaimed, we don't take
                # the action.

                if eType == 'unclaimed' and content[0] == '?':
                    fTags.add('unknown')

                name: Optional[str] = None # auto by default
                gains: Optional[str] = None
                if eType == 'action':
                    name = content
                    # TODO: Generalize action effects; also handle toggles,
                    # repeatability, etc.
                else:
                    gains = content

                actionName = takeActionInRoom(
                    exploration,
                    parseFormat,
                    name,
                    gains,
                    forwardReq,
                    backReq,
                    fTags,
                    rTags,
                    eType == 'unclaimed' # whether to leave it untaken
                )

                # Limit scope to this case
                del name
                del gains

            elif eType == 'progress':
                # If the room name hasn't been specified yet, this indicates
                # a room that we traverse en route. If the room name has
                # been specified, this is movement to a new sub-room.
                if roomName is None:
                    # Here we need to accumulate the named route, since the
                    # navigation of sub-rooms has to be figured out by
                    # pathfinding, but that's only possible once we know
                    # *all* of the listed rooms. Note that the parse
                    # format's 'runback' symbol may be used as a room name
                    # to indicate that some of the route should be
                    # auto-completed.
                    if content == parseFormat.formatDict['runback']:
                        interRoomPath.append(InterRoomEllipsis)
                    else:
                        interRoomPath.append(content)
                else:
                    # This is progress to a new sub-room. If we've been
                    # to that sub-room from the current sub-room before, we
                    # retrace the connection, and if not, we first add an
                    # unexplored connection and then explore it.
                    makeProgressInRoom(
                        exploration,
                        parseFormat,
                        content,
                        False,
                        forwardReq,
                        backReq,
                        fTags,
                        rTags
                        # annotations handled separately
                    )

            elif eType == 'frontier':
                pass
                # TODO: HERE

            elif eType == 'frontierEnd':
                pass
                # TODO: HERE

            elif eType == 'oops':
                # This removes the specified transition from the graph,
                # creating a new exploration step to do so. It tags that
                # transition as an oops in the previous graph, because
                # the transition won't exist to be tagged in the new
                # graph. If the transition led to a non-frontier unknown
                # node, that entire node is removed; otherwise just the
                # single transition is removed, along with its
                # reciprocal.
                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot mark an oops before"
                        f" we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                prev = now # remember the previous graph
                # TODO
                now = exploration.currentGraph()
                here = exploration.currentPosition()
                print("OOP", now.destinationsFrom(here))
                exploration.wait('oops') # create new step w/ no changes
                now = exploration.currentGraph()
                here = exploration.currentPosition()
                accidental = now.getDestination(here, content)
                if accidental is None:
                    raise JournalParseError(
                        f"Cannot erase transition '{content}' because it"
                        f" does not exist at decision {here}."
                    )

                accidental = cast(core.Decision, accidental)

                # If it's an unknown (the usual case) then we remove the
                # entire node
                if now.isUnknown(accidental):
                    now.remove_node(accidental)
                else:
                    # Otherwise re move the edge and its reciprocal
                    reciprocal = now.transitionReciprocal(here, content)
                    now.remove_edge(here, accidental, content)
                    if reciprocal is not None:
                        now.remove_edge(accidental, here, reciprocal)

                # Tag the transition as an oops in the step before it gets
                # removed:
                prev.tagTransition(here, content, 'oops')

            elif eType in ('oneway', 'hiddenOneway'):
                # In these cases, we create a pending progress value, since
                # it's possible to use 'oneway' as the exit from a room in
                # which case it's not in-room progress but rather a room
                # transition.
                pendingProgress = (
                    content,
                    True if eType == 'oneway' else 'hidden',
                    forwardReq,
                    backReq,
                    fTags,
                    rTags,
                    None, # No annotations need be applied now
                    None
                )

            elif eType == 'detour':
                if anonymousContent is None:
                    raise JournalParseError(
                        f"Detour on line #{lineNumber} is missing an"
                        f" anonymous room definition. Block"
                        f" is:\n{journalBlock}"
                    )
                # TODO: Support detours to existing rooms w/out anonymous
                # content...
                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot create a detour"
                        f" before we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                # First, we create an unexplored transition and then use it
                # to enter the anonymous room...
                here = exploration.currentPosition()
                now.addUnexploredEdge(
                    here,
                    content,
                    tags=fTags,
                    revTags=rTags,
                    requires=forwardReq,
                    revRequires=backReq
                )

                if roomName is None:
                    raise JournalParseError(
                        f"Detour on line #{lineNumber} occurred before room"
                        f" name was known. Block is:\n{journalBlock}"
                    )

                # Get a new unique anonymous name
                anonName = parseFormat.anonName(roomName, content)

                # Actually enter our detour room
                exploration.explore(
                    content,
                    anonName,
                    [], # No connections yet
                    content + '-return'
                )

                # Tag the new room as anonymous
                now = exploration.currentGraph()
                now.tagDecision(anonName, 'anonymous')

                # Remember transitions needed to get out of room
                thread: List[core.Transition] = []

                # Parse in-room activity and create steps for it
                anonLines = anonymousContent.splitlines()
                for anonLine in anonLines:
                    anonLine = anonLine.strip()
                    try:
                        anonType, anonContent = parseFormat.determineEntryType(
                            anonLine
                        )
                    except JournalParseError:
                        # One liner that doesn't parse -> treat as tag(s)
                        anonType = 'tag'
                        anonContent = anonLine.strip()
                        if len(anonLines) > 1:
                            raise JournalParseError(
                                f"Detour on line #{lineNumber} has multiple"
                                f" lines but one cannot be parsed as an"
                                f" entry:\n{anonLine}\nBlock"
                                f" is:\n{journalBlock}"
                            )

                    # Parse final notes, tags, and/or requirements
                    if anonType != 'note':
                        anonContent, note = parseFormat.splitFinalNote(
                            anonContent
                        )
                        anonContent, fTags, rTags = parseFormat.splitTags(
                            anonContent
                        )
                        (
                            anonContent,
                            forwardReq,
                            backReq
                        ) = parseFormat.splitRequirement(anonContent)

                    if anonType == 'note':
                        here = exploration.currentPosition()
                        now.annotateDecision(here, anonContent)
                        # We don't handle multi-line notes in anon rooms

                    elif anonType == 'tag':
                        tags = set(anonContent.split())
                        here = exploration.currentPosition()
                        now.tagDecision(here, tags)
                        if note is not None:
                            now.annotateDecision(here, note)

                    elif anonType == 'progress':
                        makeProgressInRoom(
                            exploration,
                            parseFormat,
                            anonContent,
                            False,
                            forwardReq,
                            backReq,
                            fTags,
                            rTags,
                            [ note ] if note is not None else None
                            # No reverse annotations
                        )
                        # We don't handle multi-line notes in anon rooms

                        # Remember the way back
                        # TODO: HERE Is this still accurate?
                        thread.append(anonContent + '-return')

                    elif anonType in ('pickup', 'unclaimed', 'action'):

                        if (
                            anonType == 'unclaimed'
                        and anonContent.startswith('?')
                        ):
                            fTags.add('unknown')

                        # Note: these are both type Optional[str], but since
                        # they exist in another case, they can't be
                        # explicitly typed that way here. See:
                        # https://github.com/python/mypy/issues/1174
                        name = None
                        gains = None
                        if anonType == 'action':
                            name = anonContent
                        else:
                            gains = anonContent

                        actionName = takeActionInRoom(
                            exploration,
                            parseFormat,
                            name,
                            gains,
                            forwardReq,
                            backReq,
                            fTags,
                            rTags,
                            anonType == 'unclaimed' # leave it untaken or not?
                        )

                        # Limit scope
                        del name
                        del gains

                    elif anonType == 'challenge':
                        here = exploration.currentPosition()
                        now.annotateDecision(
                            here,
                            "challenge: " + anonContent
                        )

                    elif anonType in ('blocked', 'otherway'):
                        here = exploration.currentPosition()

                        # Mark as blocked even when no explicit requirement
                        # has been provided
                        if forwardReq is None:
                            forwardReq = core.ReqImpossible()
                        if backReq is None and anonType == 'blocked':
                            backReq = core.ReqImpossible()

                        now.addUnexploredEdge(
                            here,
                            anonContent,
                            tags=fTags,
                            revTags=rTags,
                            requires=forwardReq,
                            revRequires=backReq
                        )

                    else:
                        # TODO: Any more entry types we need to support in
                        # anonymous rooms?
                        raise JournalParseError(
                            f"Detour on line #{lineNumber} includes an"
                            f" entry of type '{anonType}' which is not"
                            f" allowed in an anonymous room. Block"
                            f" is:\n{journalBlock}"
                        )

                # If we made progress, backtrack to the start of the room
                for backwards in thread:
                    exploration.retrace(backwards)

                # Now we exit back to the original room
                exploration.retrace(content + '-return')

            elif eType == 'unify': # TODO: HERE
                pass

            elif eType == 'obviate': # TODO: HERE
                # This represents a connection to somewhere we've been
                # before which is recognized but not traversed.
                # Note that when you want to use this to replace a mis-named
                # unexplored connection (which you now realize actually goes
                # to an existing sub-room, not a new one) you should just
                # oops that connection first, and then obviate to the actual
                # destination.
                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot obviate a transition"
                        f" before we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                here = exploration.currentPosition()

                # Two options: if the content lists a room:entrance combo in
                # brackets after a transition name, then it represents the
                # other side of a door from another room. If, on the other
                # hand, it just has a transition name, it represents a
                # sub-room name.
                content, otherSide = parseFormat.splitAnonymousRoom(content)

                if otherSide is None:
                    # Must be in-room progress
                    # We create (but don't explore) a transition to that
                    # sub-room.
                    baseRoom = parseFormat.baseRoomName(here)
                    currentSubPart = parseFormat.roomPartName(here)
                    if currentSubPart is None:
                        currentSubPart = parseFormat.formatDict["progress"]
                    fromDecision = parseFormat.subRoomName(
                        baseRoomName,
                        content
                    )

                    existingReciprocalDestination = now.getDestination(
                        fromDecision,
                        currentSubPart
                    )
                    # If the place we're linking to doesn't have a link back
                    # to us, then we just create a completely new link.
                    if existingReciprocalDestination is None:
                        pass
                        if now.getDestination(here, content):
                            pass
                        # TODO: HERE
                        # ISSUE: Sub-room links cannot just be named after
                        # their destination, because they might not be
                        # unique!

                    elif now.isUnknown(existingReciprocalDestination):
                        pass
                        # TODO

                    else:
                        # TODO
                        raise JournalParseError("")

                    transitionName = content + '-return'
                    # fromDecision, incoming = fromOptions[0]
                    # TODO
                else:
                    # Here the content specifies an outgoing transition name
                    # and otherSide specifies the other side, so we don't
                    # have to search for anything
                    transitionName = content

                    # Split decision name and transition name
                    fromDecision, incoming = parseFormat.parseSpecificTransition(
                        otherSide
                    )
                    dest = now.getDestination(fromDecision, incoming)

                    # Check destination exists and is unknown
                    if dest is None:
                        # TODO: Look for alternate sub-room?
                        raise JournalParseError(
                            f"Obviate entry #{lineNumber} for transition"
                            f" {content} has invalid reciprocal transition"
                            f" {otherSide}. (Did you forget to specify the"
                            f" sub-room?)"
                        )
                    elif not now.isUnknown(cast(core.Decision, dest)):
                        raise JournalParseError(
                            f"Obviate entry #{lineNumber} for transition"
                            f" {content} has invalid reciprocal transition"
                            f" {otherSide}: that transition's destination"
                            f" is already known."
                        )

                # Now that we know which edge we're obviating, do that
                # Note that while the other end is always an existing
                # transition to an unexplored destination, our end might be
                # novel, so we use replaceUnexplored from the other side
                # which allows it to do the work of creating the new
                # outgoing transition.
                now.replaceUnexplored(
                    fromDecision,
                    cast(core.Transition, incoming),
                    here,
                    transitionName,
                    requirement=backReq, # flipped
                    revRequires=forwardReq,
                    tags=rTags, # also flipped
                    revTags=fTags,
                )

            elif eType == 'challenge':
                # For now, these are just annotations
                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot annotate a challenge"
                        f" before we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                here = exploration.currentPosition()
                now.annotateDecision(here, f"{eType}: " + content)

            elif eType in ('warp', 'death'):
                # These warp the player without creating a connection
                if forwardReq or backReq:
                    raise JournalParseError(
                        f"'{eType}' entry #{lineNumber} cannot include"
                        f" requirements. Block is:\n{journalBlock}"
                    )
                if fTags or rTags:
                    raise JournalParseError(
                        f"'{eType}' entry #{lineNumber} cannot include"
                        f" tags. Block is:\n{journalBlock}"
                    )

                try:
                    exploration.warp(
                        content,
                        'death' if eType == 'death' else ''
                    )
                    # TODO: Death effects?!?
                    # TODO: We could rewind until we're in a room marked
                    # 'save' and pick up that position and even state
                    # automatically ?!? But for save-anywhere games, we'd
                    # need to have some way of marking a save (could be an
                    # entry type that creates a special wait?).
                    # There could even be a way to clone the old graph for
                    # death, since things like tags applied would presumably
                    # not be? Or maybe some would and some wouldn't?
                except KeyError:
                    raise JournalParseError(
                        f"'{eType}' entry #{lineNumber} specifies"
                        f" non-existent destination '{content}'. Block"
                        f" is:\n{journalBlock}"
                    )

            elif eType == 'runback':
                # For now, we just warp there and back
                # TODO: Actually trace the path of the runback...
                # TODO: Allow for an action to be taken at the destination
                # (like farming health, flipping a switch, etc.)
                if forwardReq or backReq:
                    raise JournalParseError(
                        f"Runback on line #{lineNumber} cannot include"
                        f" requirements. Block is:\n{journalBlock}"
                    )
                if fTags or rTags:
                    raise JournalParseError(
                        f"Runback on line #{lineNumber} cannot include tags."
                        f" Block is:\n{journalBlock}"
                    )

                # Remember where we are
                here = exploration.currentPosition()

                # Warp back to the runback point
                try:
                    exploration.warp(content, 'runaway')
                except KeyError:
                    raise JournalParseError(
                        f"Runback on line #{lineNumber} specifies"
                        f" non-existent destination '{content}'. Block"
                        f" is:\n{journalBlock}"
                    )

                # Then warp back to the current decision
                exploration.warp(here, 'runback')

            elif eType == 'traverse':
                # For now, we just warp there
                # TODO: Actually trace the path of the runback...
                if forwardReq or backReq:
                    raise JournalParseError(
                        f"Traversal on line #{lineNumber} cannot include"
                        f" requirements. Block is:\n{journalBlock}"
                    )
                if fTags or rTags:
                    raise JournalParseError(
                        f"Traversal on line #{lineNumber} cannot include tags."
                        f" Block is:\n{journalBlock}"
                    )

                if now is None:
                    raise JournalParseError(
                        f"Cannot traverse sub-rooms on line #{lineNumber}"
                        f" before exploration is started. Block"
                        f" is:\n{journalBlock}"
                    )

                # Warp to the destination
                here = exploration.currentPosition()
                destination = parseFormat.getSubRoom(now, here, content)
                if destination is None:
                    raise JournalParseError(
                        f"Traversal on line #{lineNumber} specifies"
                        f" non-existent sub-room destination '{content}' in"
                        f" room '{parseFormat.baseRoomName(here)}'. Block"
                        f" is:\n{journalBlock}"
                    )
                else:
                    exploration.warp(destination, 'traversal')

            elif eType == 'ending':
                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot annotate an ending"
                        f" before we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                if backReq:
                    raise JournalParseError(
                        f"Ending on line #{lineNumber} cannot include"
                        f" reverse requirements. Block is:\n{journalBlock}"
                    )

                # Create ending
                here = exploration.currentPosition()
                # Reverse tags are applied to the ending room itself
                now.addEnding(
                    here,
                    content,
                    tags=fTags,
                    endTags=rTags,
                    requires=forwardReq
                )
                # Transition to the ending
                print("ED RT", here, content, len(exploration))
                exploration.retrace('_e:' + content)
                print("ED RT", len(exploration))
                ended = True

            elif eType == 'tag':
                tagsToApply = set(content.split())
                if fTags or rTags:
                    raise JournalParseError(
                        f"Found tags on tag entry on line #{lineNumber}"
                        f" of block:\n{journalBlock}"
                    )

                if now is None:
                    raise JournalParseError(
                        f"On line {lineNumber}: Cannot add a tag before"
                        f" we've created the starting graph. Block"
                        f" is:\n{journalBlock}"
                    )

                here = exploration.currentPosition()
                now.tagDecision(here, tagsToApply)

            else:
                raise NotImplementedError(
                    f"Unhandled entry type '{eType}' (fix"
                    f" updateExplorationFromEntry)."
                )

            # Note: at this point, currentNote must be None. If there is an
            # end-of-line note, set up currentNote to apply that to whatever
            # is on this line.
            if note is not None:
                if eType in (
                    'entrance',
                    'exit',
                    'blocked',
                    'otherway',
                    'unexplored',
                    'unexploredOneway',
                    'progress'
                    'oneway',
                    'hiddenOneway',
                    'detour'
                ):
                    # Annotate a specific transition
                    target = (exploration.currentPosition(), content)

                elif eType in (
                    'pickup',
                    'unclaimed',
                    'action',
                ):
                    # Action name might be auto-generated
                    target = (
                        exploration.currentPosition(),
                        actionName
                    )

                else:
                    # Default: annotate current room
                    target = exploration.currentPosition()

                # Set current note value for accumulation
                currentNote = (
                    target,
                    True, # all post-entry notes count as indented
                    f"(step #{len(exploration)}) " + note
                )

        # If we ended, return None
        if ended:
            return None
        elif exitRoom is None or exitTransition is None:
            raise JournalParseError(
                f"Missing exit room and/or transition ({exitRoom},"
                f" {exitTransition}) at end of journal"
                f" block:\n{journalBlock}"
            )

        return exitRoom, exitTransition

    def observeNote(
        self,
        noteText: str,
        indented: bool = False,
        target: Optional[
            Union[core.Decision, Tuple[core.Decision, core.Transition]]
        ] = None
    ) -> None:
        """
        Observes a whole-line note in a journal, which may or may not be
        indented (level of indentation is ignored). Creates or extends
        the current pending note, or applies that note and starts a new
        one if the indentation statues or targets are different. Except
        in that case, no change is made to the exploration or its
        graphs; the annotations are actually applied when
        `applyCurrentNote` is called.

        ## Example

        >>> obs = JournalObserver()
        >>> obs.observe('[Room]\n? Left\n')
        >>> obs.observeNote('hi')
        >>> obs.observeNote('the same note')
        >>> obs.observeNote('a new note', indented=True) # different indent
        >>> obs.observeNote('another note', indented=False)
        >>> obs.observeNote('this applies to Left', target=('Room', 'Left'))
        >>> obs.observeNote('more') # same target by implication
        >>> obs.observeNote('another', target='Room') # different target
        >>> e = obs.getExploration()
        >>> m = e.currentGraph()
        >>> m.decisionAnnotations('Room') # Last note is not here yet...
        ['hi\nthe same note', 'a new note', 'another note']
        >>> m.transitionAnnotations('Room', 'Left')
        ['this applies to Left\nmore']
        >>> m.applyCurrentNote()
        >>> m.decisionAnnotations('Room') # Last note is not here yet...
        ['hi\nthe same note', 'a new note', 'another note', 'another']
        """

        # whole line is a note; handle new vs. continuing note
        if self.currentNote is None:
            # Start a new note
            if target is None:
                target = self.exploration.currentPosition()
            self.currentNote = (
                target,
                indented,
                f"(step #{len(self.exploration)}) " + noteText
            )
        else:
            # Previous note exists, use indentation & target to decide
            # if we're continuing or starting a new note
            oldTarget, wasIndented, prevText = self.currentNote
            if (
                indented != wasIndented
             or (target is not None and target != oldTarget)
            ):
                # Then we apply the old note and create a new note (at
                # the decision level by default)
                self.applyCurrentNote()
                self.currentNote = (
                    target or self.exploration.currentPosition(),
                    indented,
                    f"(step #{len(self.exploration)}) " + noteText
                )
            else:
                # Else indentation matched and target either matches or
                # was None, so add to previous note
                self.currentNote = (
                    oldTarget,
                    wasIndented,
                    prevText + '\n' + noteText
                )

    def applyCurrentNote(self) -> None:
        """
        If there is a note waiting to be either continued or applied,
        applies that note to whatever it is targeting, and clears it.
        Does nothing if there is no pending note.

        See `observeNote` for an example.
        """
        if self.currentNote is not None:
            target, _, noteText = self.currentNote
            self.currentNote = None
            # Apply our annotation to the room or transition it targets
            # TODO: Annotate the exploration instead?!?
            if isinstance(target, str):
                self.exploration.currentGraph().annotateDecision(
                    target,
                    noteText
                )
            else:
                room, transition = target
                self.exploration.currentGraph().annotateTransition(
                    room,
                    transition,
                    noteText
                )

    def makeProgressInRoom(
        self,
        subRoomName: core.Decision,
        transitionName: Optional[core.Transition] = None,
        oneway: Union[bool, str] = False,
        requires: Optional[core.Requirement] = None,
        revRequires: Optional[core.Requirement] = None,
        tags: Optional[Set[core.Tag]] = None,
        revTags: Optional[Set[core.Tag]] = None,
        annotations: Optional[List[core.Annotation]] = None,
        revAnnotations: Optional[List[core.Annotation]] = None
    ) -> None:
        """
        Updates the exploration state to indicate that movement to a new
        sub-room has occurred. Handles three cases: a
        previously-observed but unexplored sub-room, a
        never-before-observed sub-room, and a previously-visited
        sub-room. By using the parse format's progress marker (default
        '-') as the room name, a transition to the base subroom can be
        specified.

        The destination sub-room name is required, and the exploration
        object's current position will dictate which decision the player
        is currently at. If no transition name is specified, the
        transition name will be the same as the destination name (only
        the provided sub-room part) or the same as the first previous
        transition to the specified destination from the current
        location is such a transition already exists. Optional arguments
        may specify requirements, tags, and/or annotations to be applied
        to the transition, and requirements, tags, and/or annotations
        for the reciprocal transition; these will be applied in the new
        graph that results, but not retroactively. If the transition is
        a one-way transition, set `oneway` to True (default is False).
        `oneway` may also be set to the string 'hidden' to indicate a
        hidden one-way. The `newConnection` argument should be set to
        True (default False) if a new connection should be created even
        in cases where a connection already exists.

        ## Example:

        >>> obs = JournalObserver()
        >>> obs.observe("[Room]\n< T")
        >>> obs.makeProgressInRoom("subroom")
        >>> e = obs.getExploration()
        >>> len(e)
        2
        >>> e.currentPosition()
        'Room%subroom'
        >>> m = e.currentGraph()
        >>> m.destinationsFrom("Room")
        { 'T': '_u:0', 'subroom': 'Room%subroom' }
        >>> m.destinationsFrom("Room%subroom")
        { '-': 'Room' }
        >>> obs.makeProgressInRoom("-") # Back to base subroom
        >>> len(e)
        3
        >>> e.currentPosition()
        'Room'
        >>> m = e.currentGraph()
        >>> m.destinationsFrom("Room")
        { 'T': '_u:0', 'subroom': 'Room%subroom' }
        >>> m.destinationsFrom("Room%subroom")
        { '-': 'Room' }
        >>> obs.makeProgressInRoom(
        ...   "other",
        ...   oneway='hidden',
        ...   tags={"blue"},
        ...   requires=core.ReqPower("fly"),
        ...   revRequires=core.ReqAll(
        ...     core.ReqPower("shatter"),
        ...     core.ReqPower("fly")
        ...   ),
        ...   revTags={"blue"},
        ...   annotations=["Another subroom"],
        ...   revAnnotations=["This way back"],
        ... )
        >>> len(e)
        4
        >>> e.currentPosition()
        'Room%other'
        >>> m = e.currentGraph()
        >>> m.destinationsFrom("Room")
        { 'T': '_u:0', 'subroom': 'Room%subroom', 'other': 'Room%other' }
        >>> m.destinationsFrom("Room%subroom")
        { '-': 'Room' }
        >>> m.destinationsFrom("Room%other")
        { '-': 'Room' }
        >>> m.getTransitionRequirement("Room", "other")
        ReqPower('fly')
        >>> m.getTransitionRequirement("Room%other", "-")
        ReqAll(ReqPower('shatter'), ReqPower('fly'))
        >>> m.transitionTags("Room", "other")
        {'blue'}
        >>> m.transitionTags("Room%other", "-")
        {'blue'}
        >>> m.transitionAnnotations("Room", "other")
        ['Another subroom']
        >>> m.transitionAnnotations("Room%other", "-")
        ['This way back']
        >>> prevM = e.graphAtStep(-2)
        >>> prevM.destinationsFrom("Room")
        { 'T': '_u:0', 'subroom': 'Room%subroom', 'other': '_u:2' }
        >>> prevM.destinationsFrom("Room%subroom")
        { '-': 'Room' }
        >>> "Room%other" in prevM
        False
        >>> obs.makeProgressInRoom("-", transitionName="-.1", oneway=True)
        >>> len(e)
        5
        >>> e.currentPosition()
        'Room'
        >>> m = e.currentGraph()
        >>> m.destinationsFrom("Room")
        { 'T': '_u:0', 'subroom': 'Room%subroom', 'other': 'Room%other', 'other.1': 'Room%other'}
        >>> m.destinationsFrom("Room%subroom")
        { '-': 'Room' }
        >>> m.destinationsFrom("Room%other")
        { '-': 'Room', '-.1': 'Room' }
        >>> m.getTransitionRequirement("Room", "other")
        ReqPower('fly')
        >>> m.getTransitionRequirement("Room%other", "-")
        ReqAll(ReqPower('shatter'), ReqPower('fly'))
        >>> m.getTransitionRequirement("Room", "other.1")
        ReqImpossible()
        >>> m.getTransitionRequirement("Room%other", "-.1")
        ReqNothing()
        """

        # Default argument values
        if transitionName is None:
            transitionName = subRoomName
        if tags is None:
            tags = set()
        if revTags is None:
            revTags = set()
        if annotations is None:
            annotations = []
        if revAnnotations is None:
            revAnnotations = []

        # Tag the transition with 'internal' since this is in-room progress
        tags.add('internal')

        # Get current stuff
        now = self.exploration.currentGraph()
        here = self.exploration.currentPosition()
        outgoing = now.destinationsFrom(here)
        base = self.parseFormat.baseRoomName(here)
        currentSubPart = self.parseFormat.roomPartName(here)
        if currentSubPart is None:
            currentSubPart = self.parseFormat.formatDict["progress"]
        destination = self.parseFormat.subRoomName(base, subRoomName)
        isNew = destination not in now

        # Handle oneway settings (explicit requirements override them)
        if oneway is True and revRequires is None: # not including 'hidden'
            revRequires = core.ReqImpossible()

        # Did we end up creating a new subroom?
        createdSubRoom = False

        # Are we going somewhere new, or not?
        if transitionName in outgoing: # A transition we've seen before
            rev = now.transitionReciprocal(here, transitionName)
            if not now.isUnknown(destination): # Just retrace it
                self.exploration.retrace(transitionName)
            else: # previously unknown
                self.exploration.explore(
                    transitionName,
                    destination,
                    [],
                    rev # No need to worry here about collisions
                )
                createdSubRoom = True

            # And apply requirements/tags/annotations 
            now = self.exploration.currentGraph()
            now.tagTransition(here, transitionName, tags)
            now.annotateTransition(here, transitionName, annotations)
            if requires is not None:
                now.setTransitionRequirement(
                    here,
                    transitionName,
                    requires
                )
            if rev is not None:
                now.tagTransition(destination, rev, revTags)
                now.annotateTransition(destination, rev, revAnnotations)
                if revRequires is not None:
                    now.setTransitionRequirement(
                        destination,
                        rev,
                        revRequires
                    )

        else: # A new connection
            # Add an unexplored edge and then explore it
            now.addUnexploredEdge(
                here,
                transitionName,
                tags=tags,
                annotations=annotations,
                requires=requires,
                revTags=revTags,
                revAnnotations=revAnnotations,
                revRequires=revRequires
            )

            # Find a unique name for the returning connection
            rev = currentSubPart
            linksThere = now.destinationsFrom(destination)
            while rev in linksThere:
                suffix = rev[len(currentSubPart):]
                if suffix == '':
                    suffix = '.1'
                else:
                    suffix = '.' + str(int(suffix[1:]) + 1)
                rev = currentSubPart + suffix

            # Explore the unknown we just created
            self.exploration.explore(
                transitionName,
                destination,
                [],
                rev # No need to worry here about collisions
            )
            createdSubRoom = True

        # If we created this subroom, need to update any previous
        # unexplored links to it to point to the decision we just
        # created
        if createdSubRoom:
            # Find all places where we've listed an unexplored connection to
            # the sub-room being visited.
            now = self.exploration.currentGraph()
            allSubs = self.parseFormat.allSubRooms(now, here)
            unexploredLinksToDestination = set()
            for sub in allSubs:
                # Note: we use the sub-room-name as is as the transition
                # name, because when setting up unexplored links we don't
                # know whether they go to sub-rooms or not, so we name the
                # using the entire content of their entries.
                if subRoomName in outgoing:
                    unexploredLinksToDestination.add(sub)

        # If the destination is already an established sub-room:
        if not isNew:
            if len(unexploredLinksToDestination) > 0:
                raise JournalParseError(
                    "While heading to an explored sub-room, found a new"
                    " unexplored link to that sub-room: '{subRoomName}'"
                    " has unexplored links {unexploredLinksToDestination}"
                )

            # If there's already a link, we just re-traverse that link
            if subRoomName in outgoing:
                self.exploration.retrace(subRoomName)
            else:
                # If there's not yet a link to the existing destination
                # node, add an unexplored node and then immediately
                # explore that link as a return to the existing
                # destination node
                now.addUnexploredEdge(
                    here,
                    subRoomName,
                    tags=tags,
                    annotations=annotations,
                    requires=requires,
                    revTags=revTags,
                    revAnnotations=revAnnotations,
                    revRequires=revRequires
                )
                reciprocal = None
                if currentSubPart in now.destinationsFrom(destination):
                    reciprocal = currentSubPart
                    # We are handling one of these so remove it:
                    unexploredLinksToDestination.remove(destination)
                # Update the exploration
                self.exploration.returnTo(
                    subRoomName,
                    destination,
                    reciprocal
                )

            # Overwrite requirements, tags, and annotations
            # based on any new info. TODO: Warn if new info is
            # mismatched with old info?
            newGraph = self.exploration.currentGraph()
            newPos = self.exploration.currentPosition()
            if requires is not None:
                self.exploration.updateRequirementNow(
                    here,
                    subRoomName,
                    requires
                )
            newGraph.tagTransition(here, subRoomName, tags)
            newGraph.annotateTransition(here, subRoomName, annotations)

            # A hidden oneway sets ReqImpossible, but only on the step after
            # the transition is taken
            if oneway == 'hidden' and revRequires is None:
                revRequires = core.ReqImpossible()

            # If there's a reciprocal, apply any specified tags,
            # annotations, and/or requirements to it.
            reciprocal = newGraph.transitionReciprocal(here, subRoomName)
            if reciprocal is not None:
                newGraph.tagTransition(newPos, reciprocal, revTags)
                newGraph.annotateTransition(
                    newPos,
                    reciprocal,
                    revAnnotations
                )
                if revRequires is not None:
                    newGraph.setTransitionRequirement(
                        newPos,
                        reciprocal,
                        revRequires
                    )

        else:
            # Completely novel sub-room
            # First we add an unexplored transition with the sub-part name,
            # then we explore it

            # A hidden oneway applies both explicit and implied transition
            # requirements only after the transition has been taken
            if oneway == "hidden":
                postRevReq: Optional[core.Requirement] = None
                if revRequires is None:
                    postRevReq = core.ReqImpossible()
                else:
                    postRevReq = revRequires
                revRequires = None

            now.addUnexploredEdge(
                here,
                subRoomName,
                tags=tags,
                annotations=annotations,
                requires=requires,
                revTags=revTags,
                revAnnotations=revAnnotations,
                revRequires=revRequires
            )
            self.exploration.explore(
                subRoomName,
                destination,
                [],
                currentSubPart
            )

            # Update the reciprocal edge requirements
            now = self.exploration.currentGraph()
            there = self.exploration.currentPosition()
            reciprocal = now.transitionReciprocal(here, subRoomName)
            if oneway == "hidden" and reciprocal is not None:
                self.exploration.updateRequirementNow(
                    there,
                    reciprocal,
                    postRevReq
                )

            # At this point, we also need to take all previously-unexplored
            # links to this sub-room and connect them to the explored room
            # we just created. TODO: Make it so that those links all go to
            # the same single unknown node so that you can just use that
            # node above!!!
            for otherSub in unexploredLinksToDestination:
                now.replaceUnexplored(
                    otherSub,
                    subRoomName,
                    destination,
                    currentSubPart
                )


    def takeActionInRoom(
        self,
        name: Optional[core.Transition] = None,
        gain: Optional[str] = None,
        forwardReq: Optional[core.Requirement] = None,
        extraGain: Optional[core.Requirement] = None,
        fTags: Optional[Set[core.Tag]] = None,
        rTags: Optional[Set[core.Tag]] = None,
        untaken: bool = False
    ) -> core.Transition:
        """
        Adds an action to the current room, and takes it. The exploration to
        modify and the parse format to use are required. If a name for the
        action is not provided, a unique name will be generated. If the
        action results in gaining an item, the item gained should be passed
        as a string (will be parsed using `ParseFormat.parseItem`).
        Forward/backward requirements and tags may be provided, but passing
        anything other than None for the backward requirement or tags will
        result in a `JournalParseError`.

        If `untaken` is set to True (default is False) then the action will
        be created, but will not be taken.

        Returns the name of the transition, which is either the specified
        name or a unique name created automatically.
        """
        # Get current info
        here = exploration.currentPosition()
        now = exploration.currentGraph()

        # Assign a unique action name if none was provided
        wantsUnique = False
        if name is None:
            wantsUnique = True
            name = f"action@{len(exploration)}"

        # Accumulate powers/tokens gained
        gainedStuff = []
        # Parse item gained if there is one, and add it to the action name
        # as well
        if gain is not None:
            gainedStuff.append(parseFormat.parseItem(gain))
            name += gain

        # Reverse requirements are translated into extra powers/tokens gained
        # (but may only be a disjunction of power/token requirements).
        # TODO: Allow using ReqNot to instantiate power-removal/token-cost
        # effects!!!
        if extraGain is not None:
            gainedStuff.extend(extraGain.asGainList())

        if len(gainedStuff) > 0:
            effects = core.effects(gain=gainedStuff)
        else:
            effects = core.effects() # no effects

        # Ensure that action name is unique
        if wantsUnique:
            # Find all transitions that start with this name which have a
            # '.' in their name.
            already = [
                transition
                for transition in cast(
                    Dict[str, str],
                    now.destinationsFrom(here)
                )
                if transition.startswith(name) and '.' in transition
            ]

            # Collect just the numerical parts after the dots
            nums = []
            for prev in already:
                try:
                    nums.append(int(prev.split('.')[-1]))
                except ValueError:
                    pass

            # If there aren't any (or aren't any with a .number part), make
            # the name unique by adding '.1'
            if len(nums) == 0:
                name = name + '.1'
            else:
                # If there are nums, pick a higher one
                name = name + '.' + str(max(nums) + 1)

        # TODO: Handle repeatable actions with effects, and other effect
        # types...

        if rTags:
            raise JournalParseError(
                f"Cannot apply reverse tags {rTags} to action '{name}' in"
                f" room {here}: Actions have no reciprocal."
            )

        # Create and/or take the action
        if untaken:
            now.addAction(
                here,
                name,
                forwardReq, # might be None
                effects
            )
        else:
            exploration.takeAction(
                name,
                forwardReq, # might be None
                effects
            )

        # Apply tags to the action transition
        if fTags is not None:
            now = exploration.currentGraph()
            now.tagTransition(here, name, fTags)

        # Return the action name
        return name


def updateExplorationFromEntry(
    exploration: core.Exploration,
    parseFormat: ParseFormat,
    journalBlock: str,
    enterFrom: Optional[Tuple[core.Decision, core.Transition]] = None,
) -> Optional[Tuple[core.Decision, core.Transition]]:
    """
    Given an exploration object, a parsing format dictionary, and a
    multi-line string which is a journal entry block, updates the
    exploration to reflect the entries in the block. Except for the
    first block of a journal, or continuing blocks after an ending,
    where `enterFrom` must be None, a tuple specifying the room and
    transition taken to enter the block must be provided so we know where
    to anchor the new activity.

    This function returns a tuple specifying the room and transition in
    that room taken to exit from the block, which can be used as the
    `enterFrom` value for the next block. It returns none if the block
    ends with an 'ending' entry.
    """
    # Set up state variables

    # Tracks the room name, once one has been declared
    roomName: Optional[core.Decision] = None
    roomTags: Set[core.Tag] = set()

    # Whether we've seen an entrance/exit yet
    seenEntrance = False

    # The room & transition used to exit
    exitRoom = None
    exitTransition = None

    # This tracks the current note text, since notes can continue across
    # multiple lines
    currentNote: Optional[Tuple[
        Union[core.Decision, Tuple[core.Decision, core.Transition]], # target
        bool, # was this note indented?
        str # note text
    ]] = None

    # Tracks a pending progress step, since things like a oneway can be
    # used for either within-room progress OR room-to-room transitions.
    pendingProgress: Optional[Tuple[
        core.Transition, # transition name to create
        Union[bool, str], # is it one-way; 'hidden' for a hidden one-way?
        Optional[core.Requirement], # requirement for the transition
        Optional[core.Requirement], # reciprocal requirement
        Optional[Set[core.Tag]], # tags to apply
        Optional[Set[core.Tag]], # reciprocal tags
        Optional[List[core.Annotation]], # annotations to apply
        Optional[List[core.Annotation]] # reciprocal annotations
    ]] = None

    # This tracks the current entries in an inter-room abbreviated path,
    # since we first have to accumulate all of them and then do
    # pathfinding to figure out a concrete inter-room path.
    interRoomPath: List[Union[Type[InterRoomEllipsis], core.Decision]] = []

    # Standardize newlines just in case
    journalBlock = journalBlock\
        .replace('\r\n', '\n')\
        .replace('\n\r', '\n')\
        .replace('\r', '\n')

    # Line splitting variables
    lineNumber = 0 # first iteration will increment to 1 before use
    blockIndex = 0 # Character index into the block tracking progress
    blockLen = len(journalBlock) # So we know when to stop
    lineIncrement = 1 # How many lines we've processed

    # Tracks presence of an end entry, which must be final in the block
    # except for notes or tags.
    ended = False

    # Parse each line separately, but collect multiple lines for
    # multi-line detours
    while blockIndex < blockLen:
        lineNumber += lineIncrement
        lineIncrement = 1
        try:
            # Find the next newline
            nextNL = journalBlock.index('\n', blockIndex)
            line = journalBlock[blockIndex:nextNL]
            blockIndex = nextNL + 1
        except ValueError:
            # If there isn't one, rest of the block is the next line
            line = journalBlock[blockIndex:]
            blockIndex = blockLen

        print("LL", lineNumber, line)

        # Check for and split off anonymous room content
        line, anonymousContent = parseFormat.splitAnonymousRoom(line)
        if (
            anonymousContent is None
        and parseFormat.startsAnonymousRoom(line)
        ):
            endIndex = parseFormat.anonymousRoomEnd(
                journalBlock,
                blockIndex
            )
            if endIndex is None:
                raise JournalParseError(
                    f"Anonymous room started on line {lineNumber}"
                    f" was never closed in block:\n{journalBlock}"
                )
            anonymousContent = journalBlock[nextNL + 1:endIndex].strip()
            # TODO: Is this correct?
            lineIncrement = anonymousContent.count('\n') + 1
            # Skip to end of line where anonymous room ends
            blockIndex = journalBlock.index('\n', endIndex + 1)

            # Trim the start of the anonymous room from the line end
            line = line.rstrip()[:-1]

        # Skip blank lines
        if not line.strip():
            continue

        # Check for indentation (mostly ignored, but important for
        # comments).
        indented = line[0] == ' '

        # Strip indentation going forward
        line = line.strip()

        # Detect entry type and separate content
        eType, eContent = parseFormat.determineEntryType(line)

        print("EE", lineNumber, eType, eContent)

        if exitTransition is not None and eType != 'note':
            raise JournalParseError(
                f"Entry after room exit on line {lineNumber} in"
                f" block:\n{journalBlock}"
            )

        if eType != 'detour' and anonymousContent is not None:
            raise JournalParseError(
                f"Entry #{lineNumber} with type {eType} does not"
                f" support anonymous room content. Block"
                f" is:\n{journalBlock}"
            )

        # Handle note creation
        if currentNote is not None and eType != 'note':
            # This ends a note, so we can apply the pending note and
            # reset it.
            target, _, noteText = currentNote
            currentNote = None
            # Apply our annotation to the room or transition it targets
            if isinstance(target, str):
                exploration.currentGraph().annotateDecision(target, noteText)
            else:
                room, transition = target
                exploration.currentGraph().annotateTransition(
                    room,
                    transition,
                    noteText
                )
        elif eType == 'note':
            # whole line is a note; handle new vs. continuing note
            if currentNote is None:
                # Start a new note
                currentNote = (
                    exploration.currentPosition(),
                    indented,
                    eContent
                )
            else:
                # Previous note exists, use indentation to decide if
                # we're continuing or starting a new note
                target, wasIndented, noteText = currentNote
                if indented != wasIndented:
                    # Then we apply the old note and create a new note at
                    # the room level
                    if isinstance(target, str):
                        exploration.currentGraph().annotateDecision(
                            target,
                            noteText
                        )
                    else:
                        room, transition = target
                        exploration.currentGraph().annotateTransition(
                            room,
                            transition,
                            noteText
                        )
                    currentNote = (
                        exploration.currentPosition(),
                        indented,
                        f"(step #{len(exploration)}) " + eContent
                    )
                else:
                    # Else indentation matches so add to previous note
                    currentNote = (
                        target,
                        wasIndented,
                        noteText + '\n' + eContent
                    )
            # In (only) this case, we've handled the entire line
            continue

        # Handle a pending progress step if there is one
        if pendingProgress is not None:
            # Any kind of entry except a note (which we would have hit
            # above and continued) indicates that a progress marker is
            # in-room progress rather than being a room exit.
            makeProgressInRoom(exploration, parseFormat, *pendingProgress)

            # Clean out pendingProgress
            pendingProgress = None

        # Check for valid eType if pre-room
        if roomName is None and eType not in ('room', 'progress'):
            raise JournalParseError(
                f"Invalid entry #{lineNumber}: Entry type '{eType}' not"
                f" allowed before room name. Block is:\n{journalBlock}"
            )

        # Check for valid eType if post-room
        if ended and eType not in ('note', 'tag'):
            raise JournalParseError(
                f"Invalid entry #{lineNumber}: Entry type '{eType}' not"
                f" allowed after an ending. Block is:\n{journalBlock}"
            )

        # Parse a line-end note if there is one
        # Note that note content will be handled after we handle main
        # entry stuff
        content, note = parseFormat.splitFinalNote(eContent)

        # Parse a line-end tags section if there is one
        content, fTags, rTags = parseFormat.splitTags(content)

        # Parse a line-end requirements section if there is one
        content, forwardReq, backReq = parseFormat.splitRequirement(content)

        # Strip any remaining whitespace from the edges of our content
        content = content.strip()

        # Get current graph
        now = exploration.getCurrentGraph()

        # This will trigger on the first line in the room, and handles
        # the actual room creation in the graph
        handledEntry = False # did we handle the entry in this block?
        if roomName is not None and not seenEntrance:
            # We're looking for an entrance and if we see anything else
            # except a tag, we'll assume that the entrance is implicit,
            # and give an error if we don't have an implicit entrance
            # set up. If the entrance is explicit, we'll give a warning
            # if it doesn't match the previous entrance for the same
            # prior-room exit from last time.
            if eType in ('entrance', 'otherway'):
                # An explicit entrance; must match previous associated
                # entrance if there was one.

                # An otherway marker can be used as an entrance to
                # indicate that the connection is one-way. Note that for
                # a one-way connection, we may have a requirement
                # specifying that the reverse connection exists but
                # can't be traversed yet. In cases where there is no
                # requirement, we *still* add a reciprocal edge to the
                # graph, but mark it as `ReqImpossible`. This is because
                # we want the rooms' adjacency to be visible from both
                # sides, and some of our graph algorithms have to respect
                # requirements anyways. Cases where a reciprocal edge
                # will be absent are one-way teleporters where there's
                # actually no sealed connection indicator in the
                # destination room. TODO: Syntax for those?

                # Get transition name
                transitionName = content

                # If this is not the start of the exploration or a
                # reset after an ending, check for a previous transition
                # entering this decision from the same previous
                # room/transition.
                prevReciprocal = None
                prevDestination = None
                if enterFrom is not None and now is not None:
                    fromDecision, fromTransition = enterFrom
                    prevReciprocal = now.transitionReciprocal(
                        fromDecision,
                        fromTransition
                    )
                    prevDestination = cast(
                        core.Decision,
                        now.getDestination(
                            fromDecision,
                            fromTransition
                        )
                    )
                    if prevDestination is None:
                        raise JournalParseError(
                            f"Transition {fromTransition} from"
                            f" {fromDecision} was named as exploration"
                            f" point but has not been created!"
                        )

                    # If there is a previous reciprocal edge marked, and
                    # it doesn't match the entering reciprocal edge,
                    # that's an inconsistency, unless that edge was
                    # coming from an unknown node.
                    if (
                        not now.isUnknown(prevDestination)
                    and prevReciprocal != transitionName
                    ): # prevReciprocal of None won't be
                        warnings.warn(
                            (
                                f"Explicit incoming transition from"
                                f" {fromDecision}:{fromTransition}"
                                f" entering {roomName} via"
                                f" {transitionName} does not match"
                                f" previous entrance point for that"
                                f" transition, which was"
                                f" {prevReciprocal}. The reciprocal edge"
                                f" will NOT be updated."
                            ),
                            JournalParseWarning
                        )

                    # Similarly, if there is an outgoing transition in
                    # the destination room whose name matches the
                    # declared reciprocal but whose destination isn't
                    # unknown and isn't he current location, that's an
                    # inconsistency
                    prevRevDestination = now.getDestination(
                        roomName,
                        transitionName
                    )
                    if (
                        prevRevDestination is not None
                    and not now.isUnknown(
                            cast(core.Decision, prevRevDestination)
                        )
                    and prevRevDestination != fromDecision
                    ):
                        warnings.warn(
                            (
                                f"Explicit incoming transition from"
                                f" {fromDecision}:{fromTransition}"
                                f" entering {roomName} via"
                                f" {transitionName} does not match"
                                f" previous destination for"
                                f" {transitionName} in that room, which was"
                                f" {prevRevDestination}. The reciprocal edge"
                                f" will NOT be updated."
                                # TODO: What will happen?
                            ),
                            JournalParseWarning
                        )

                seenEntrance = True
                handledEntry = True
                if enterFrom is None or now is None:
                    # No incoming transition info
                    if len(exploration) == 0:
                        # Start of the exploration
                        exploration.start(roomName, [])
                        # with an explicit entrance.
                        exploration.currentGraph().addUnexploredEdge(
                            roomName,
                            transitionName,
                            tags=fTags,
                            revTags=rTags,
                            requires=forwardReq,
                            revRequires=backReq
                        )
                    else:
                        # Continuing after an ending MUST NOT involve an
                        # explicit entrance, because the transition is a
                        # warp. To annotate a warp where the character
                        # enters back into the game using a traversable
                        # transition (and e.g., transition effects
                        # apply), include a block noting their presence
                        # on the other side of that doorway followed by
                        # an explicit transition into the room where
                        # control is available, with a 'forced' tag. If
                        # the other side is unknown, just use an
                        # unexplored entry as the first entry in the
                        # block after the ending.
                        raise JournalParseError(
                            f"On line #{lineNumber}, an explicit"
                            f" entrance is not allowed because the"
                            f" previous block ended with an ending."
                            f" Block is:\n{journalBlock}"
                        )
                else:
                    # Implicitly, prevDestination must not be None here,
                    # since a JournalParseError would have been raised
                    # if enterFrom was not None and we didn't get a
                    # prevDestination. But it might be an unknown area.
                    prevDestination = cast(core.Decision, prevDestination)

                    # Extract room & transition we're entering from
                    fromRoom, fromTransition = enterFrom

                    # If we've seen this room before, check for an old
                    # transition destination, since we might implicitly
                    # be entering a sub-room.
                    if now is not None and roomName in now:
                        if now.isUnknown(prevDestination):
                            # The room already exists, but the
                            # transition we're taking to enter it is not
                            # one we've used before. If the entry point
                            # is not a known transition, unless the
                            # journaler has explicitly tagged the
                            # reciprocal transition with 'discovered', we
                            # assume entrance is to a new sub-room, since
                            # otherwise the transition should have been
                            # known ahead of time.
                            # TODO: Does this mean we have to search for
                            # matching names in other sub-room parts
                            # when doing in-room transitions... ?
                            exploration.returnTo(
                                fromTransition,
                                roomName,
                                transitionName
                            )
                        else:
                            # We already know where this transition
                            # leads
                            exploration.retrace(fromTransition)
                    else:
                        # We're entering this room for the first time.
                        exploration.explore(
                            fromTransition,
                            roomName,
                            [],
                            transitionName
                        )
                    # Apply forward tags to the outgoing transition
                    # that's named, and reverse tags to the incoming
                    # transition we just followed
                    now = exploration.currentGraph() # graph was updated
                    here = exploration.currentPosition()
                    now.tagTransition(here, transitionName, fTags)
                    now.tagTransition(fromRoom, fromTransition, rTags)

            elif eType == 'tag':
                roomTags |= set(content.split())
                if fTags or rTags:
                    raise JournalParseError(
                        f"Found tags on tag entry on line #{lineNumber}"
                        f" of block:\n{journalBlock}"
                    )
                # don't do anything else here since it's a tag;
                # seenEntrance remains False
                handledEntry = True

            else:
                # For any other entry type, it counts as an implicit
                # entrance. We need to follow that transition, or if an
                # appropriate link does not already exist, raise an
                # error.
                seenEntrance = True
                # handledEntry remains False in this case

                # Check that the entry point for this room can be
                # deduced, and deduce it so that we can figure out which
                # sub-room we're actually entering...
                if enterFrom is None:
                    if len(exploration) == 0:
                        # At the start of the exploration, there's often
                        # no specific transition we come from, which is
                        # fine.
                        exploration.start(roomName, [])
                    else:
                        # Continuation after an ending
                        exploration.warp(roomName, 'restart')
                else:
                    fromDecision, fromTransition = enterFrom
                    prevReciprocal = None
                    if now is not None:
                        prevReciprocal = now.transitionReciprocal(
                            fromDecision,
                            fromTransition
                        )
                    if prevReciprocal is None:
                        raise JournalParseError(
                            f"Implicit transition into room {roomName}"
                            f" is invalid because no reciprocal"
                            f" transition has been established for exit"
                            f" {fromTransition} in previous room"
                            f" {fromDecision}."
                        )

                    # In this case, we retrace the transition, and if
                    # that fails because of a ValueError (e.g., because
                    # that transition doesn't exist yet or leads to an
                    # unknown node) then we'll raise the error as a
                    # JournalParseError.
                    try:
                        exploration.retrace(fromTransition)
                    except ValueError as e:
                        raise JournalParseError(
                            f"Implicit transition into room {roomName}"
                            f" is invalid because:\n{e.args[0]}"
                        )

                    # Note: no tags get applied here, because this is an
                    # implicit transition, so there's no room to apply
                    # new tags. An explicit transition could be used
                    # instead to update transition properties.

        # Previous block may have updated the current graph
        now = exploration.getCurrentGraph()

        # At this point, if we've seen an entrance we're in the right
        # room, so we should apply accumulated room tags
        if seenEntrance and roomTags:
            if now is None:
                raise RuntimeError(
                    "Inconsistency: seenEntrance is True but the current"
                    " graph is None."
                )

            here = exploration.currentPosition()
            now.tagDecision(here, roomTags)
            roomTags = set() # reset room tags

        # Handle all entry types not handled above (like note)
        if handledEntry:
            # We skip this if/else but still do end-of-loop cleanup
            pass

        elif eType == 'note':
            raise RuntimeError("Saw 'note' eType in lower handling block.")

        elif eType == 'room':
            if roomName is not None:
                raise ValueError(
                    f"Multiple room names detected on line {lineNumber}"
                    f" in block:\n{journalBlock}"
                )

            # Setting the room name changes the loop state
            roomName = content

            # These will be applied later
            roomTags = fTags

            if rTags:
                raise JournalParseError(
                    f"Reverse tags cannot be applied to a room"
                    f" (found tags {rTags} for room '{roomName}')."
                )

        elif eType == 'entrance':
            # would be handled above if seenEntrance was false
            raise JournalParseError(
                f"Multiple entrances on line {lineNumber} in"
                f" block:\n{journalBlock}"
            )

        elif eType == 'exit':
            # We note the exit transition and will use that as our
            # return value. This also will cause an error on the next
            # iteration if there are further non-note entries in the
            # journal block
            exitRoom = exploration.currentPosition()
            exitTransition = content

            # At this point we add an unexplored edge for this exit,
            # assuming it's not one we've seen before. Note that this
            # does not create a new exploration step (that will happen
            # later).
            knownDestination = None
            if now is not None:
                knownDestination = now.getDestination(
                    exitRoom,
                    exitTransition
                )

                if knownDestination is None:
                    now.addUnexploredEdge(
                        exitRoom,
                        exitTransition,
                        tags=fTags,
                        revTags=rTags,
                        requires=forwardReq,
                        revRequires=backReq
                    )

                else:
                    # Otherwise just apply any tags to the transition
                    now.tagTransition(exitRoom, exitTransition, fTags)
                    existingReciprocal = now.transitionReciprocal(
                        exitRoom,
                        exitTransition
                    )
                    if existingReciprocal is not None:
                        now.tagTransition(
                            cast(core.Decision, knownDestination),
                            existingReciprocal,
                            rTags
                        )

        elif eType in (
            'blocked',
            'otherway',
            'unexplored',
            'unexploredOneway',
        ):
            # Simply add the listed transition to our current room,
            # leading to an unknown destination, without creating a new
            # exploration step
            transition = content
            here = exploration.currentPosition()

            # If there isn't a listed requirement, infer ReqImpossible
            # where appropriate
            if forwardReq is None and eType in ('blocked', 'otherway'):
                forwardReq = core.ReqImpossible()
            if backReq is None and eType in ('blocked', 'unexploredOneway'):
                backReq = core.ReqImpossible()

            # TODO: What if we've annotated a known source for this
            # link?

            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot create an unexplored"
                    f" transition before we've created the starting"
                    f" graph. Block is:\n{journalBlock}"
                )

            now.addUnexploredEdge(
                here,
                transition,
                tags=fTags,
                revTags=rTags,
                requires=forwardReq,
                revRequires=backReq
            )

        elif eType in ('pickup', 'unclaimed', 'action'):
            # We both add an action to the current room, and then take
            # that action, or if the type is unclaimed, we don't take
            # the action.

            if eType == 'unclaimed' and content[0] == '?':
                fTags.add('unknown')

            name: Optional[str] = None # auto by default
            gains: Optional[str] = None
            if eType == 'action':
                name = content
                # TODO: Generalize action effects; also handle toggles,
                # repeatability, etc.
            else:
                gains = content

            actionName = takeActionInRoom(
                exploration,
                parseFormat,
                name,
                gains,
                forwardReq,
                backReq,
                fTags,
                rTags,
                eType == 'unclaimed' # whether to leave it untaken
            )

            # Limit scope to this case
            del name
            del gains

        elif eType == 'progress':
            # If the room name hasn't been specified yet, this indicates
            # a room that we traverse en route. If the room name has
            # been specified, this is movement to a new sub-room.
            if roomName is None:
                # Here we need to accumulate the named route, since the
                # navigation of sub-rooms has to be figured out by
                # pathfinding, but that's only possible once we know
                # *all* of the listed rooms. Note that the parse
                # format's 'runback' symbol may be used as a room name
                # to indicate that some of the route should be
                # auto-completed.
                if content == parseFormat.formatDict['runback']:
                    interRoomPath.append(InterRoomEllipsis)
                else:
                    interRoomPath.append(content)
            else:
                # This is progress to a new sub-room. If we've been
                # to that sub-room from the current sub-room before, we
                # retrace the connection, and if not, we first add an
                # unexplored connection and then explore it.
                makeProgressInRoom(
                    exploration,
                    parseFormat,
                    content,
                    False,
                    forwardReq,
                    backReq,
                    fTags,
                    rTags
                    # annotations handled separately
                )

        elif eType == 'frontier':
            pass
            # TODO: HERE

        elif eType == 'frontierEnd':
            pass
            # TODO: HERE

        elif eType == 'oops':
            # This removes the specified transition from the graph,
            # creating a new exploration step to do so. It tags that
            # transition as an oops in the previous graph, because the
            # transition won't exist to be tagged in the new graph. If the
            # transition led to a non-frontier unknown node, that entire
            # node is removed; otherwise just the single transition is
            # removed, along with its reciprocal.
            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot mark an oops before"
                    f" we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            prev = now # remember the previous graph
            # TODO
            now = exploration.currentGraph()
            here = exploration.currentPosition()
            print("OOP", now.destinationsFrom(here))
            exploration.wait('oops') # create new step w/ no changes
            now = exploration.currentGraph()
            here = exploration.currentPosition()
            accidental = now.getDestination(here, content)
            if accidental is None:
                raise JournalParseError(
                    f"Cannot erase transition '{content}' because it"
                    f" does not exist at decision {here}."
                )

            accidental = cast(core.Decision, accidental)

            # If it's an unknown (the usual case) then we remove the
            # entire node
            if now.isUnknown(accidental):
                now.remove_node(accidental)
            else:
                # Otherwise re move the edge and its reciprocal
                reciprocal = now.transitionReciprocal(here, content)
                now.remove_edge(here, accidental, content)
                if reciprocal is not None:
                    now.remove_edge(accidental, here, reciprocal)

            # Tag the transition as an oops in the step before it gets
            # removed:
            prev.tagTransition(here, content, 'oops')

        elif eType in ('oneway', 'hiddenOneway'):
            # In these cases, we create a pending progress value, since
            # it's possible to use 'oneway' as the exit from a room in
            # which case it's not in-room progress but rather a room
            # transition.
            pendingProgress = (
                content,
                True if eType == 'oneway' else 'hidden',
                forwardReq,
                backReq,
                fTags,
                rTags,
                None, # No annotations need be applied now
                None
            )

        elif eType == 'detour':
            if anonymousContent is None:
                raise JournalParseError(
                    f"Detour on line #{lineNumber} is missing an"
                    f" anonymous room definition. Block"
                    f" is:\n{journalBlock}"
                )
            # TODO: Support detours to existing rooms w/out anonymous
            # content...
            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot create a detour"
                    f" before we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            # First, we create an unexplored transition and then use it
            # to enter the anonymous room...
            here = exploration.currentPosition()
            now.addUnexploredEdge(
                here,
                content,
                tags=fTags,
                revTags=rTags,
                requires=forwardReq,
                revRequires=backReq
            )

            if roomName is None:
                raise JournalParseError(
                    f"Detour on line #{lineNumber} occurred before room"
                    f" name was known. Block is:\n{journalBlock}"
                )

            # Get a new unique anonymous name
            anonName = parseFormat.anonName(roomName, content)

            # Actually enter our detour room
            exploration.explore(
                content,
                anonName,
                [], # No connections yet
                content + '-return'
            )

            # Tag the new room as anonymous
            now = exploration.currentGraph()
            now.tagDecision(anonName, 'anonymous')

            # Remember transitions needed to get out of room
            thread: List[core.Transition] = []

            # Parse in-room activity and create steps for it
            anonLines = anonymousContent.splitlines()
            for anonLine in anonLines:
                anonLine = anonLine.strip()
                try:
                    anonType, anonContent = parseFormat.determineEntryType(
                        anonLine
                    )
                except JournalParseError:
                    # One liner that doesn't parse -> treat as tag(s)
                    anonType = 'tag'
                    anonContent = anonLine.strip()
                    if len(anonLines) > 1:
                        raise JournalParseError(
                            f"Detour on line #{lineNumber} has multiple"
                            f" lines but one cannot be parsed as an"
                            f" entry:\n{anonLine}\nBlock"
                            f" is:\n{journalBlock}"
                        )

                # Parse final notes, tags, and/or requirements
                if anonType != 'note':
                    anonContent, note = parseFormat.splitFinalNote(
                        anonContent
                    )
                    anonContent, fTags, rTags = parseFormat.splitTags(
                        anonContent
                    )
                    (
                        anonContent,
                        forwardReq,
                        backReq
                    ) = parseFormat.splitRequirement(anonContent)

                if anonType == 'note':
                    here = exploration.currentPosition()
                    now.annotateDecision(here, anonContent)
                    # We don't handle multi-line notes in anon rooms

                elif anonType == 'tag':
                    tags = set(anonContent.split())
                    here = exploration.currentPosition()
                    now.tagDecision(here, tags)
                    if note is not None:
                        now.annotateDecision(here, note)

                elif anonType == 'progress':
                    makeProgressInRoom(
                        exploration,
                        parseFormat,
                        anonContent,
                        False,
                        forwardReq,
                        backReq,
                        fTags,
                        rTags,
                        [ note ] if note is not None else None
                        # No reverse annotations
                    )
                    # We don't handle multi-line notes in anon rooms

                    # Remember the way back
                    # TODO: HERE Is this still accurate?
                    thread.append(anonContent + '-return')

                elif anonType in ('pickup', 'unclaimed', 'action'):

                    if (
                        anonType == 'unclaimed'
                    and anonContent.startswith('?')
                    ):
                        fTags.add('unknown')

                    # Note: these are both type Optional[str], but since
                    # they exist in another case, they can't be
                    # explicitly typed that way here. See:
                    # https://github.com/python/mypy/issues/1174
                    name = None
                    gains = None
                    if anonType == 'action':
                        name = anonContent
                    else:
                        gains = anonContent

                    actionName = takeActionInRoom(
                        exploration,
                        parseFormat,
                        name,
                        gains,
                        forwardReq,
                        backReq,
                        fTags,
                        rTags,
                        anonType == 'unclaimed' # leave it untaken or not?
                    )

                    # Limit scope
                    del name
                    del gains

                elif anonType == 'challenge':
                    here = exploration.currentPosition()
                    now.annotateDecision(
                        here,
                        "challenge: " + anonContent
                    )

                elif anonType in ('blocked', 'otherway'):
                    here = exploration.currentPosition()

                    # Mark as blocked even when no explicit requirement
                    # has been provided
                    if forwardReq is None:
                        forwardReq = core.ReqImpossible()
                    if backReq is None and anonType == 'blocked':
                        backReq = core.ReqImpossible()

                    now.addUnexploredEdge(
                        here,
                        anonContent,
                        tags=fTags,
                        revTags=rTags,
                        requires=forwardReq,
                        revRequires=backReq
                    )

                else:
                    # TODO: Any more entry types we need to support in
                    # anonymous rooms?
                    raise JournalParseError(
                        f"Detour on line #{lineNumber} includes an"
                        f" entry of type '{anonType}' which is not"
                        f" allowed in an anonymous room. Block"
                        f" is:\n{journalBlock}"
                    )

            # If we made progress, backtrack to the start of the room
            for backwards in thread:
                exploration.retrace(backwards)

            # Now we exit back to the original room
            exploration.retrace(content + '-return')

        elif eType == 'unify': # TODO: HERE
            pass

        elif eType == 'obviate': # TODO: HERE
            # This represents a connection to somewhere we've been
            # before which is recognized but not traversed.
            # Note that when you want to use this to replace a mis-named
            # unexplored connection (which you now realize actually goes
            # to an existing sub-room, not a new one) you should just
            # oops that connection first, and then obviate to the actual
            # destination.
            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot obviate a transition"
                    f" before we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            here = exploration.currentPosition()

            # Two options: if the content lists a room:entrance combo in
            # brackets after a transition name, then it represents the
            # other side of a door from another room. If, on the other
            # hand, it just has a transition name, it represents a
            # sub-room name.
            content, otherSide = parseFormat.splitAnonymousRoom(content)

            if otherSide is None:
                # Must be in-room progress
                # We create (but don't explore) a transition to that
                # sub-room.
                baseRoom = parseFormat.baseRoomName(here)
                currentSubPart = parseFormat.roomPartName(here)
                if currentSubPart is None:
                    currentSubPart = parseFormat.formatDict["progress"]
                fromDecision = parseFormat.subRoomName(
                    baseRoomName,
                    content
                )

                existingReciprocalDestination = now.getDestination(
                    fromDecision,
                    currentSubPart
                )
                # If the place we're linking to doesn't have a link back
                # to us, then we just create a completely new link.
                # TODO
            else:
                # Here the content specifies an outgoing transition name
                # and otherSide specifies the other side, so we don't
                # have to search for anything
                transitionName = content

                # Split decision name and transition name
                fromDecision, incoming = parseFormat.parseSpecificTransition(
                    otherSide
                )
                dest = now.getDestination(fromDecision, incoming)

                # Check destination exists and is unknown
                if dest is None:
                    # TODO: Look for alternate sub-room?
                    raise JournalParseError(
                        f"Obviate entry #{lineNumber} for transition"
                        f" {content} has invalid reciprocal transition"
                        f" {otherSide}. (Did you forget to specify the"
                        f" sub-room?)"
                    )
                elif not now.isUnknown(cast(core.Decision, dest)):
                    raise JournalParseError(
                        f"Obviate entry #{lineNumber} for transition"
                        f" {content} has invalid reciprocal transition"
                        f" {otherSide}: that transition's destination"
                        f" is already known."
                    )

            # Now that we know which edge we're obviating, do that
            # Note that while the other end is always an existing
            # transition to an unexplored destination, our end might be
            # novel, so we use replaceUnexplored from the other side
            # which allows it to do the work of creating the new
            # outgoing transition.
            now.replaceUnexplored(
                fromDecision,
                cast(core.Transition, incoming),
                here,
                transitionName,
                requirement=backReq, # flipped
                revRequires=forwardReq,
                tags=rTags, # also flipped
                revTags=fTags,
            )

        elif eType == 'challenge':
            # For now, these are just annotations
            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot annotate a challenge"
                    f" before we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            here = exploration.currentPosition()
            now.annotateDecision(here, f"{eType}: " + content)

        elif eType in ('warp', 'death'):
            # These warp the player without creating a connection
            if forwardReq or backReq:
                raise JournalParseError(
                    f"'{eType}' entry #{lineNumber} cannot include"
                    f" requirements. Block is:\n{journalBlock}"
                )
            if fTags or rTags:
                raise JournalParseError(
                    f"'{eType}' entry #{lineNumber} cannot include"
                    f" tags. Block is:\n{journalBlock}"
                )

            try:
                exploration.warp(
                    content,
                    'death' if eType == 'death' else ''
                )
                # TODO: Death effects?!?
                # TODO: We could rewind until we're in a room marked
                # 'save' and pick up that position and even state
                # automatically ?!? But for save-anywhere games, we'd
                # need to have some way of marking a save (could be an
                # entry type that creates a special wait?).
                # There could even be a way to clone the old graph for
                # death, since things like tags applied would presumably
                # not be? Or maybe some would and some wouldn't?
            except KeyError:
                raise JournalParseError(
                    f"'{eType}' entry #{lineNumber} specifies"
                    f" non-existent destination '{content}'. Block"
                    f" is:\n{journalBlock}"
                )

        elif eType == 'runback':
            # For now, we just warp there and back
            # TODO: Actually trace the path of the runback...
            # TODO: Allow for an action to be taken at the destination
            # (like farming health, flipping a switch, etc.)
            if forwardReq or backReq:
                raise JournalParseError(
                    f"Runback on line #{lineNumber} cannot include"
                    f" requirements. Block is:\n{journalBlock}"
                )
            if fTags or rTags:
                raise JournalParseError(
                    f"Runback on line #{lineNumber} cannot include tags."
                    f" Block is:\n{journalBlock}"
                )

            # Remember where we are
            here = exploration.currentPosition()

            # Warp back to the runback point
            try:
                exploration.warp(content, 'runaway')
            except KeyError:
                raise JournalParseError(
                    f"Runback on line #{lineNumber} specifies"
                    f" non-existent destination '{content}'. Block"
                    f" is:\n{journalBlock}"
                )

            # Then warp back to the current decision
            exploration.warp(here, 'runback')

        elif eType == 'traverse':
            # For now, we just warp there
            # TODO: Actually trace the path of the runback...
            if forwardReq or backReq:
                raise JournalParseError(
                    f"Traversal on line #{lineNumber} cannot include"
                    f" requirements. Block is:\n{journalBlock}"
                )
            if fTags or rTags:
                raise JournalParseError(
                    f"Traversal on line #{lineNumber} cannot include tags."
                    f" Block is:\n{journalBlock}"
                )

            if now is None:
                raise JournalParseError(
                    f"Cannot traverse sub-rooms on line #{lineNumber}"
                    f" before exploration is started. Block"
                    f" is:\n{journalBlock}"
                )

            # Warp to the destination
            here = exploration.currentPosition()
            destination = parseFormat.getSubRoom(now, here, content)
            if destination is None:
                raise JournalParseError(
                    f"Traversal on line #{lineNumber} specifies"
                    f" non-existent sub-room destination '{content}' in"
                    f" room '{parseFormat.baseRoomName(here)}'. Block"
                    f" is:\n{journalBlock}"
                )
            else:
                exploration.warp(destination, 'traversal')

        elif eType == 'ending':
            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot annotate an ending"
                    f" before we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            if backReq:
                raise JournalParseError(
                    f"Ending on line #{lineNumber} cannot include"
                    f" reverse requirements. Block is:\n{journalBlock}"
                )

            # Create ending
            here = exploration.currentPosition()
            # Reverse tags are applied to the ending room itself
            now.addEnding(
                here,
                content,
                tags=fTags,
                endTags=rTags,
                requires=forwardReq
            )
            # Transition to the ending
            print("ED RT", here, content, len(exploration))
            exploration.retrace('_e:' + content)
            print("ED RT", len(exploration))
            ended = True

        elif eType == 'tag':
            tagsToApply = set(content.split())
            if fTags or rTags:
                raise JournalParseError(
                    f"Found tags on tag entry on line #{lineNumber}"
                    f" of block:\n{journalBlock}"
                )

            if now is None:
                raise JournalParseError(
                    f"On line {lineNumber}: Cannot add a tag before"
                    f" we've created the starting graph. Block"
                    f" is:\n{journalBlock}"
                )

            here = exploration.currentPosition()
            now.tagDecision(here, tagsToApply)

        else:
            raise NotImplementedError(
                f"Unhandled entry type '{eType}' (fix"
                f" updateExplorationFromEntry)."
            )

        # Note: at this point, currentNote must be None. If there is an
        # end-of-line note, set up currentNote to apply that to whatever
        # is on this line.
        if note is not None:
            if eType in (
                'entrance',
                'exit',
                'blocked',
                'otherway',
                'unexplored',
                'unexploredOneway',
                'progress'
                'oneway',
                'hiddenOneway',
                'detour'
            ):
                # Annotate a specific transition
                target = (exploration.currentPosition(), content)

            elif eType in (
                'pickup',
                'unclaimed',
                'action',
            ):
                # Action name might be auto-generated
                target = (
                    exploration.currentPosition(),
                    actionName
                )

            else:
                # Default: annotate current room
                target = exploration.currentPosition()

            # Set current note value for accumulation
            currentNote = (
                target,
                True, # all post-entry notes count as indented
                f"(step #{len(exploration)}) " + note
            )

    # If we ended, return None
    if ended:
        return None
    elif exitRoom is None or exitTransition is None:
        raise JournalParseError(
            f"Missing exit room and/or transition ({exitRoom},"
            f" {exitTransition}) at end of journal"
            f" block:\n{journalBlock}"
        )

    return exitRoom, exitTransition
