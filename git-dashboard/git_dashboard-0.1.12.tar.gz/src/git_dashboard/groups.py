# Git Dashboard
# Copyright (C) 2022 Jung Ko <kojung@gmail.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of  MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Groups is a collection of Group (see group.py). Underlying model is a dictionary
of groups. E.g.
    groups = {
        "group1": [
            ["name1", "branch1", "status1", "path1"],
            ["name2", "branch2", "status2", "path2"],
            ...
        ],
        "group2": [
            ["name3", "branch3", "status3", "path3"],
        ]
    }
"""

from PySide6.QtWidgets import QTabWidget

from git_dashboard.group import (
    GroupView,
    GroupModel
)

class GroupsView(QTabWidget):
    """View class for groups"""
    def __init__(self, groups, args):
        """constructor"""
        super().__init__()
        self.groups = groups

        self.setTabPosition(QTabWidget.West)
        self.setMovable(True)

        self.models = {}
        for name, group in groups.items():
            model = GroupModel(group)
            view  = GroupView(model, args)
            self.addTab(view, name)
            self.models[name] = model
