# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.assess.adjusted_span import AdjustedSpan
from contrast.agent.assess.assess_exceptions import ContrastAssessException

BELOW = "BELOW"
LOW_SPAN = "LOW_SPAN"
WITHIN = "WITHIN"
WITHOUT = "WITHOUT"
HIGH_SPAN = "HIGH_SPAN"
ABOVE = "ABOVE"


class Tag(object):
    def __init__(self, length, start_index=0):
        self.start_index = 0
        self.end_index = 0
        self.length = 0

        self.update_range(start_index, start_index + length)

    def __str__(self):
        return f"[{self.start_index},{self.end_index}]"

    def __repr__(self):
        return f"Tag({self.start_index} - {self.end_index}, {self.length})"

    def __len__(self):
        return self.length

    def __eq__(self, other):
        return (
            self.start_index == other.start_index and self.end_index == other.end_index
        )

    def update_range(self, start_index, end_index):
        if start_index < 0:
            raise ContrastAssessException("Unable to set start index negative")

        if end_index < start_index:
            raise ContrastAssessException("Unable to set start index after end index")

        self.start_index = start_index
        self.end_index = end_index

        self.length = end_index - start_index

    def covers(self, index):
        """
        Return true if the tag covers the given position in the string
        """
        return self.start_index <= index < self.end_index

    def range(self):
        # slice is exclusive on the end
        return slice(self.start_index, self.end_index + 1, 1)

    def overlaps(self, other):
        """
        Return True if Tag's overlap in range else False
        :param other: Tag object to compare
        :return: boolean
        """
        if (
            self.start_index < other.start_index <= self.end_index
        ):  # we start below other & end in it
            return True

        if (
            self.start_index >= other.start_index and self.end_index <= other.end_index
        ):  # we start and end in other
            return True

        if (
            self.start_index <= other.end_index < self.end_index
        ):  # we start in other & end above it
            return True

        return False

    def to_span(self, shift=0):
        return AdjustedSpan(self.start_index + shift, self.end_index + shift)

    # These methods shift or set new indexes on the existing Tag object
    def shift(self, index):
        self.update_range(self.start_index + index, self.end_index + index)

    def shift_end(self, index):
        self.update_range(self.start_index, self.end_index + index)

    def set_start(self, start_index):
        self.update_range(start_index, self.end_index)

    def set_end(self, end_index):
        self.update_range(self.start_index, end_index)

    def compare_range(self, start, stop):
        """
        The tag is ______ the range
        rrrrrrr == self.range, the range of the tag
        """
        result = None

        # r starts and stops below
        # rrrrrrrrrrrrr
        #               start       stop
        if self.start_index < start and self.end_index <= start:
            result = BELOW
        # r starts below and finishes within
        # rrrrrrrrrrrrr
        #    start       stop
        if self.start_index < start < self.end_index <= stop:
            result = LOW_SPAN
        # r is between start and stop
        #        rrrrrrrrrrrrrrr
        # start                   stop
        if start <= self.start_index < stop and self.end_index <= stop:
            result = WITHIN
            # r starts below and finishes above stop
        #  rrrrrrrrrrrrrrrrrrrrrrrr
        #     start       stop
        if self.start_index < start and self.end_index > stop:
            result = WITHOUT
            # r starts within and finishes above stop
        #           rrrrrrrrrrrrr
        #   start       stop
        if start <= self.start_index < stop < self.end_index:
            result = HIGH_SPAN
        # starts and stops above
        #                   rrrrrrrrrrrrr
        #  start       stop
        if self.start_index >= stop and self.end_index > stop:
            result = ABOVE

        return result

    def merge(self, other):
        """
        Given a tag, merge its ranges with this one
        such that the lowest start and highest end
        become the values of this tag

        :param other: Tag
        :return: True if the other tag was merged into
        """
        if not self.overlaps(other):
            return False

        start = min(self.start_index, other.start_index)
        finish = max(self.end_index, other.end_index)

        self.update_range(start, finish)

        return True

    def intersect(self, other):
        """
        Given a tag, intersect its ranges with this one
        such that the highest start and lowest end become
        the values of this tag.

        :param other: Tag
        :return: True if the resulting tag has nonzero length
        """
        if not self.overlaps(other):
            return False

        start = max(self.start_index, other.start_index)
        finish = min(self.end_index, other.end_index)

        if start == finish:
            # tags that are directly adjacent no not intersect
            return False

        self.update_range(start, finish)

        return True

    def copy_modified(self, shift):
        """
        Modification to tracked String can change the position and length of the tracked tag

        :param shift: integer value, negative value moves left
        :return: new Tag that has updated indexes
        """
        start = self.start_index + shift

        new_start_index = start if start >= 0 else 0

        new_length = self.length if start >= 0 else (self.length + start)

        return Tag(new_length, new_start_index)
