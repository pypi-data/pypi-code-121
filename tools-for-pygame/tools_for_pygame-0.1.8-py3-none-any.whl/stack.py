#!/usr/bin/env python3

from typing import Any
from .exceptions import EmptyStackError


class Node:
    def __init__(self, val: Any):
        self.val = val
        self.next = None

    # deletes all the values in a cascade when calling Stack.clear
    def __del__(self):
        del self.val
        del self.next


class Stack:
    """
    Stack

    Type: class

    Description: a stack where you can push or pop items from and that
        you can iterate from the first item on the stack to the last

    Args:
        any number of arguments is accepted and the value will be put
        into the stack from last to first, therefor the first value
        given will be the first value on the stack
        >>> a = Stack(1, 2, 3, 4)
        >>> a
        Stack(1, 2, 3, 4)
        >>> a.peek()
        1

    Properties:
        'is_empty' (bool, readonly): if the stack has no items

    Magic methods:
        '__len__()' (int): returns the size of the stack
        '__str__()' (str): gives a string representation of the stack

    Methods:
        'push(val)' (None): pushes a value on the stack
        'pop()' (Any): pops a value off the stack, returning it
        'peek() (Any)': returns the topmost value of the stack
        'clear()' (None): empties the stack
    """
    def __init__(self, *values):
        self.__head__ = Node(None)
        self.__size__ = 0
        self.__current_node__ = self.__head__

        for val in reversed(values):
            self.push(val)

    def __len__(self):
        return self.__size__

    def __str__(self):
        output = ""
        node = self.__head__

        while node.next:
            output += f"{node.next.val}, "
            node = node.next

        return f"Stack({output[:-2]})"

    @property
    def is_empty(self):
        return self.__size__ == 0

    def clear(self) -> None:
        del self.__head__.next
        self.__head__.next = None
        self.__size__ = 0

    def push(self, val: Any) -> None:
        node = Node(val)
        node.next = self.__head__.next
        self.__head__.next = node
        self.__size__ += 1

    def pop(self) -> Any:
        if self.is_empty:
            raise EmptyStackError("cannot pop items from an empty stack")

        popped_node = self.__head__.next
        self.__head__.next = self.__head__.next.next
        self.__size__ -= 1
        return popped_node.val

    def peek(self) -> Any:
        if self.is_empty:
            raise EmptyStackError("cannot peek from an empty stack")
        return self.__head__.next.val

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__current_node__.next:
            self.__current_node__ = self.__head__
            raise StopIteration

        val = self.__current_node__.next.val
        self.__current_node__ = self.__current_node__.next

        return val
