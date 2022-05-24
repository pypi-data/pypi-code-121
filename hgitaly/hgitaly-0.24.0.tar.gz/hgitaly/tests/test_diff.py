# Copyright 2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later

from hgitaly.service.diff import (
    CurrDiff,
    Limits,
    Parser,
)


def test_parser_corner_cases():
    parser = Parser(Limits(), CurrDiff())
    parser.parse([b""])
