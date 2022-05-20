# Copyright (c) 2021-2022 Johnathan P. Irvin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from typing import Iterable

from ..data import TerrainNodeData
from ..events import Event
from ..sdk import EventEnum, aw_terrain_next, aw_terrain_query, aw_wait


class TerrainQuery:
    def __init__(self, instance: "Instance") -> None:
        """
        Initializes the query.

        Args:
            instance (Instance): The instance to run the query on.
        """        
        self._instance = instance
        self._sequence = None

    def on_receive_terrain(self, event: Event) -> None:
        """
        This is the callback that is called when an object is found in a cell.

        Args:
            event (Event): The event that was triggered.
        """
        self.data.append(
            TerrainNodeData(
                node_x=event.terrain_node_x,
                node_z=event.terrain_node_z,
                node_size=event.terrain_node_size,
                heights=event.terrain_node_heights,
                textures=event.terrain_node_textures
            )
        )

    def query_specific(self, **kwargs) -> Iterable[TerrainNodeData]:
        """
        Queries the specific x, z coordinates.

        Args:
            x (int): The x coordinate to query.
            z (int): The z coordinate to query.

        Returns:
            Iterable[TerrainNodeData]: The result of the query.
        """
        x, z = kwargs.get("x"), kwargs.get("z")

        self.data = []
        self._instance.bus.subscribe(
            EventEnum.AW_EVENT_TERRAIN_DATA,
            self.on_receive_terrain
        )

        while not aw_terrain_query(
            x, z, self._sequence
        ):
            aw_wait(1)

        self._instance.bus.unsubscribe(
            EventEnum.AW_EVENT_TERRAIN_DATA,
            self.on_receive_terrain
        )
        return self.data

    def query_all(self) -> Iterable[TerrainNodeData]:
        """
        Queries all the data.

        Returns:
            Iterable[TerrainNodeData]: The result of the query.
        """
        self.data = []
        self._instance.bus.subscribe(
            EventEnum.AW_EVENT_TERRAIN_DATA,
            self.on_receive_terrain
        )

        while not aw_terrain_next():
            aw_wait(1)

        self._instance.bus.unsubscribe(
            EventEnum.AW_EVENT_TERRAIN_DATA,
            self.on_receive_terrain
        )
        return self.data

    def query(self, **kwargs) -> Iterable[TerrainNodeData]:
        """
        Queries the terrain.

        Args:
            x (int): The x coordinate to query.
            z (int): The z coordinate to query.

        Returns:
            Iterable[TerrainNodeData]: The result of the query.
        """
        if kwargs.get("x") != None and kwargs.get("z") != None:
            return self.query_specific(**kwargs)

        return self.query_all()
