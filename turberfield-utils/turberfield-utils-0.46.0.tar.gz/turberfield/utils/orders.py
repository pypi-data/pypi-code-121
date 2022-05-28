#!/usr/bin/env python
# encoding: UTF-8

# This file is part of turberfield.
#
# Turberfield is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Turberfield is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with turberfield.  If not, see <http://www.gnu.org/licenses/>.


class Orders:

    registry = {}

    @classmethod
    def register(cls):
        """
        Use this decorator to register a function for ordered execution.

        """
        def decorator(method):
            method.n = Orders.registry.setdefault(
                method.__name__, len(Orders.registry)
            )
            return method
        return decorator

    @property
    def methods(self):
        """
        Return a sequence of 2-tuples; (name, method).

        This property gives you all the object's registered methods in the order
        they were defined.

        """
        return [
            (name, obj)
            for name, obj in [
                (name, getattr(self, name))
                for name in dir(self)
                if name != "methods"
            ]
            if callable(obj) and hasattr(obj, "n") and not isinstance(obj, type)
        ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sequence = sorted([(obj.n, name) for name, obj in self.methods])
