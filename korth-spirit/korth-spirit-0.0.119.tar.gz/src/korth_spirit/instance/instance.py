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
from dataclasses import dataclass, field
from typing import Any, List

from ..data import LoginData, StateChangeData
from ..events import EventBus
from ..query import QueryEnum, QueryFactory
from ..sdk import (aw_create, aw_destroy, aw_enter, aw_instance_set, aw_login,
                   aw_say, aw_state_change, aw_wait, aw_whisper)


@dataclass
class Instance:
    name: str
    bus: EventBus = field(init=False, repr=False, default_factory=EventBus)

    def __enter__(self) -> "Instance":
        self._instance = aw_create()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        aw_instance_set(self._instance)
        aw_destroy(self._instance)

    def login(self, citizen_number: int, password: str) -> "Instance":
        """
        Login to the universe.

        Returns:
            Instance: The instance.
        """
        aw_login(self._instance, LoginData(
            citizen=citizen_number,
            password=password,
            app_name=f'Python Wrapped Application #{citizen_number}',
            bot_name=self.name
        ))

        return self
    
    def enter(self, world: str) -> "Instance":
        """
        Enter the specified world.

        Args:
            world (str): The name of the world.

        Returns:
            Instance: The instance.
        """
        aw_instance_set(self._instance)
        aw_enter(world)
        return self

    def move_to(self, x: int, y: int, z: int) -> "Instance":
        """
        Move to the specified coordinates.

        Args:
            x (int): The x coordinate.
            y (int): The y coordinate.
            z (int): The z coordinate.

        Returns:
            Instance: The instance.
        """
        aw_state_change(self._instance, StateChangeData(x=x, y=y, z=z))

        return self

    def say(self, message: str) -> "Instance":
        """
        Say something.

        Args:
            message (str): The message.

        Returns:
            Instance: The instance.
        """
        aw_instance_set(self._instance)
        aw_say(message)
        return self

    def whisper(self, session: int, message: str) -> "Instance":
        """
        Whisper something.

        Args:
            session (int): The session to whisper to.
            message (str): The message.

        Returns:
            Instance: The instance.
        """
        aw_instance_set(self._instance)
        aw_whisper(session, message)
        
        return self

    def query(self, query_type: QueryEnum = QueryEnum.OBJECT, **kwargs) -> List[Any]:
        """
        Make a query from the instance.

        Args:
            query_type (QueryEnum, optional): The query type. Defaults to QueryEnum.OBJECT.
            **kwargs: The query arguments.

        Returns:
            List[Any]: The query results.
        """        
        aw_instance_set(self._instance)

        return QueryFactory(self, query_type)(**kwargs)

    def main_loop(self, timer: int = 100) -> None:
        """
        Run the main loop.

        Args:
            timer (int, optional): The timer interval in milliseconds. Defaults to 100.
        """
        while True:
            aw_wait(timer)
