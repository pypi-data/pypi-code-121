"""Define and manipulate trends."""
# pylint: disable=fixme

import random
from copy import deepcopy
from dataclasses import dataclass
from operator import gt as falling_trend
from operator import lt as rising_trend
from typing import Callable, Iterable, List, Optional, Sequence, Tuple


def _gen_random(nrands: int = 1, seed: float = None, rot: int = 0) -> Iterable:
    """Generate sequences of random floats
    Ignoring flake8 warning S311 about pseudo-random-number generators.
    I want a pseudo-random number generator!

    seed permits a reproduceable "random" sequence
    rot permits yielding the numbers in a different (rotated) order,
        e.g., rot=2 will give the numbers in the order
        "3rd, 4th, ... nth, 0th, 1st, 2nd"

    Args:
        nrands: how many to yield
        seed: where to start (random number generator seed)
        rot: how many positions to rotate the sequence before starting

    Yields:
        Random floats generated from the seed.
    """
    random.seed(seed)

    rot = rot % nrands if nrands else 0  # in case rot > nrands or nrand == 0
    for _ in range(rot):
        random.random()  # noqa: S311

    for _ in range(nrands - rot):
        rand = random.random()  # noqa: S311
        yield rand

    random.seed(seed)
    for _ in range(rot):
        rand = random.random()  # noqa: S311
        yield rand

    # and reset the random number generator
    random.seed()  # noqa: S311


@dataclass
class Trend:
    """Represent a single trend.

    Attributes:
        average: The trend's average.
        length: The trend's length. (default: 1)

    Raises:
        TypeError: Length is not an int
        ValueError: Length is not positive

    """

    average: float
    length: int = 1

    def __post_init__(self):
        """Validate the object.

        Raises:
            TypeError: Length is not an int
            ValueError: Length is not positive

        """
        if not isinstance(self.average, (int, float)):
            raise TypeError("average must be number")
        self.average = float(self.average)
        if not isinstance(self.length, int):
            raise TypeError("length must be integer")
        if self.length <= 0:
            raise ValueError("length must be positive")

    def __eq__(self, other) -> bool:
        """Equal averages.

        Args:
            other: RHS of the comparison.

        Returns:
            Whether the two averages are equal.

        """
        return self.average == other.average

    def __ge__(self, other) -> bool:
        """Left average greater than or equal to right.

        Args:
            other: RHS of the comparison.

        Returns:
            True iff the RHS average is not larger.

        """
        return self.average >= other.average

    def __gt__(self, other) -> bool:
        """Left average greater than right.

        Args:
            other: RHS of the comparison.

        Returns:
            True iff the RHS average is smaller.

        """
        return self.average > other.average

    def __le__(self, other) -> bool:
        """Left average less than or equal to right.

        Args:
            other: RHS of the comparison.

        Returns:
            True iff the RHS average is not smaller.

        """
        return self.average <= other.average

    def __lt__(self, other) -> bool:
        """Left average less than right.

        Args:
            other: RHS of the comparison.

        Returns:
            True iff the RHS average is larger.

        """
        return self.average < other.average

    def __str__(self) -> str:
        """Convert to a nice string to display.

        Returns:
            The string "(length, average)"

        """
        return f"({str(self.length)}, {self.average:.1f})"

    def __add__(self, other) -> "Trend":
        """Combine two Trends into one.

        Args:
            other: the Trend to add

        Returns:
            A Trend with the combined length, and the weighted average of the averages.

        """
        length = self.length + other.length
        average = (self.total() + other.total()) / length
        # TODO: generalize
        return Trend(average=average, length=length)

    def __iadd__(self, other) -> "Trend":
        """Assimilate another Trend.

        Args:
            other: the Trend to assimilate.

        Returns:
            The two objects combined into one.

        """
        new = self + other
        self.average = new.average
        self.length = new.length
        return self

    def total(self) -> float:
        """Sum the Trend.

        Returns:
            Total of all elements that make up the trend.

        """
        # TODO: generalize
        return self.average * self.length


def _average_merge(  # noqa: C901_
    list_of_trends, trend, are_one_trend: Callable = rising_trend
) -> List[Trend]:
    """Append a new trend.

    Merge a Trend into a simple list of Trend objects. (*Not* a Trendlist.)
    Recursively merges with the rightmost Trend object,
    then continues recursively.

    Args:
        list_of_trends: list to merge into
        trend: Trend to merge from right
        are_one_trend: operator to decide whether two Trend() objects can merge
            are_one_trend(left, right) == the left and right trends can merge

    Raises:
        TypeError: element of starting list or object being merged are non-Trend objects
        ValueError: merging elements have the same averages

    Returns:
        The merged list, recursively merged to create maximal decomposition.

    """
    # typechecks
    if not isinstance(trend, Trend):
        raise TypeError("merging element must be Trend")
    if not all(isinstance(elem, Trend) for elem in list_of_trends):
        raise TypeError("non-Trend in list")
    # null case
    if not list_of_trends:  # if the object's still empty
        list_of_trends.append(trend)
        return list_of_trends
    right = list_of_trends.pop()
    if right == trend:
        raise ValueError("trend averages must differ!")
    if are_one_trend(right, trend):  # merge and recurse
        right = right + trend
        list_of_trends = _average_merge(list_of_trends, right, are_one_trend)
    else:  # new trend cannot merge
        list_of_trends.append(right)
        list_of_trends.append(trend)
    return list_of_trends


class Trendlist(list):
    """A list of trends.

    Note that this sub-classes list.

    """

    def __init__(
        self,
        list_of_trends: Optional[List["Trend"]] = None,
        are_one_trend: Callable = rising_trend,
    ) -> None:
        """Create and initalize list of Trend objects, uniquely decomposed.

        By default, creates a list of increasing-Trend objects.
        N.B., After initialization,
            averages of the trend objects will decrease monotonically!
        If, in adjacent Trend objects,
            the RH object has a greater average than its LH neighbor,
            the two Trend objects will simply merge.
        If the operator is falling_trend,
            the list will contain decreasing-Trend objects,
            and the averages in the list will increase monotonically.

        Args:
            list_of_trends: A simple list of Trend objects
            are_one_trend: operator to decide whether two Trend() objects can merge
                are_one_trend(left, right) == the left and right trends can merge

        """
        elements: Sequence = []
        if list_of_trends:
            for trend in list_of_trends:
                elements = _average_merge(elements, trend, are_one_trend)
        super().__init__(elements)

    def __str__(self) -> str:
        """Return a nice, string representation.

        Returns:
            A string with at most six Trend objects
            If six or fewer, print all the objects
            If longer print the first three, an elipsis ("..."), and the last three.

        """
        if len(self) < 7:  # print whole thing
            plist = [str(elem) for elem in self]
        else:  # just print first and last three
            plist = [str(elem) for elem in (self[:3] + self[-3:])]
            plist.insert(3, "...")
        printable = "["
        printable += ", ".join(plist)
        printable += "]"
        return printable

    def append(self, trend: Trend, are_one_trend: Callable = rising_trend) -> None:
        """Append a new trend, an in-place operation.

        No return value, but the original object with a new Trend appended.
        Merge objects as required.

        Raises:
            TypeError: object being merged not a Trend
            ValueError: merging elements have the same averages

        Args:
            trend: Trend object to stick on the right end
            are_one_trend: operator to decide whether two Trend() objects can merge
                are_one_trend(left, right) == the left and right trends can merge

        """
        if not isinstance(trend, Trend):
            raise TypeError("merging element must be Trend")
        if not self:  # if the object's still empty
            super().append(trend)
            return
        right = self.pop()
        if right == trend:
            raise ValueError("trend averages must differ!")
        assert not right == trend
        if are_one_trend(right, trend):  # merge and recurse
            right = right + trend
            self.append(right, are_one_trend)
        else:  # new trend cannot merge
            super().append(right)
            super().append(trend)
        return

    def rotate(self, are_one_trend: Callable = rising_trend) -> "Trendlist":
        """Move the leftmost trend to the right end.

        Args:
            are_one_trend: operator to decide whether two Trend() objects can merge
                are_one_trend(left, right) == the left and right trends can merge

        Returns:
            New Trendlist object, merged recursively as required.

        """
        if len(self) < 2:
            return self
        left = self[0]
        right = deepcopy(Trendlist(self[1:]))
        right.append(left, are_one_trend=are_one_trend)
        return right

    def lengths(self) -> List[int]:
        """Just the lengths.

        Returns:
            List of lengths of all constituent Trend objects.

        """
        return [elem.length for elem in self]

    def averages(self) -> List[float]:
        """Just the averages.

        Returns:
            List of averages of all constituent Trend objects.

        """
        return [elem.average for elem in self]

    def rotate_to_single_trend(self) -> Tuple[int, int]:
        """Rotate until there's a single trend.

        Returns:
            # of rotations needed: int
            location of beginning of trend in initial sequence: int

        """
        nrot = 0
        pos_start = 0
        trendlist = deepcopy(self)
        while len(trendlist) > 1:
            assert len(trendlist) != 1  # noqa: S101
            pos_start += trendlist[0].length
            trendlist = trendlist.rotate()
            nrot += 1
        return pos_start, nrot


def decompose(  # noqa: C901
    seq: Iterable[float], direction: str = "both"
) -> Tuple["Trendlist", "Trendlist"]:
    """Decompose seq into both increasing and decreasing trends.

    Args:
        seq_length: length of the random sequence
        direction: "up" to create just increasing trend, "down" to create decreasing,
            "both" to return both.

    Raises:
        ValueError: direction not in {'up', 'down', 'both'}

    Returns:
        Two decompositions of sequence into maximal Trend objects:
            increasing and decreasing
        If "up" or "down", one of the Trendlist returned is empty.

    """
    if direction not in {"up", "down", "both"}:
        raise ValueError("direction must be in {'up', 'down', 'both'}")

    inc_trends = Trendlist()
    dec_trends = Trendlist()
    for elem in seq:
        trend = Trend(average=elem)
        if direction != "down":
            inc_trends.append(trend, rising_trend)
        if direction != "up":
            dec_trends.append(trend, falling_trend)
    return inc_trends, dec_trends


def random_trends(  # noqa: C901
    seq_length: int, direction: str = "both", seed: float = None, rot: int = 0
) -> Tuple["Trendlist", "Trendlist"]:
    """Decompose random sequence into both increasing and decreasing trends.

    Args:
        seq_length: length of the random sequence
        direction: "up" to return just increasing trend, "down" to return decreasing,
            "both" to return both.
        seed: a fixed seed to start the random number generator.
            Default, "None", uses a random seed.
        rot: how far to rotate the random sequence
            before decomposing it into maximal Trend objects

    Raises:
        ValueError: direction not in {'up', 'down', 'both'}

    Returns:
        Two decompositions of sequence into maximal Trend objects:
            increasing and decreasing
        If "up" or "down", one of the Trendlist returned is empty.

    """
    random_sequence = _gen_random(nrands=seq_length, seed=seed, rot=rot)
    return decompose(random_sequence, direction=direction)
