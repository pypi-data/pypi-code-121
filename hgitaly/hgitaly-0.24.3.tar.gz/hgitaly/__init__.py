# Copyright 2020-2021 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from pathlib import Path


__version__ = Path(__file__).with_name('VERSION').read_text().strip()  # noqa F401
