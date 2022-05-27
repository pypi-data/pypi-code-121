from typing import Optional, Any

class Node:
    def __init__(
        self,
        data: Optional[Any] = None):
        self._data = data
        self._prev = None
        self._next = None

    @property
    def data(self):
        return self._data
    
    @property
    def prev(self):
        return self._prev
    
    @prev.setter
    def prev(self, value):
        self._prev = value

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        self._next = value

class LinkedList:
    def __init__(
        self,
        node: Optional[Node] = None):
        self.count = 0

        if node:
            self.head = node

            self.incr()

            pointer = node
            while pointer.next:
                pointer = pointer.next
                self.incr()

    def incr(self):
        self.count += 1

    def get_tail(
        self,
        node: Optional[Node] = None):
        if self.count == 0:
            return None

        pointer = node if node else self.head

        if pointer.next is None:
            return pointer
        else:
            return self.get_tail(pointer.next)

    def append(
        self,
        node: Node):
        if self.count != 0:
            tail = self.get_tail(self.head)
            tail.next = node
        else:
            self.head = node

        self.incr()
        return node

    def set_next(
        self,
        current_node: Node,
        node: Node):
        # Save current state
        pointer = current_node
        original_next = pointer.next

        # Set the next node
        pointer.next = node
        node.prev = pointer

        # In case of original next node is not null
        # Set the previous of original next node to new node
        if original_next:
            original_next.prev = node
            node.next = original_next

        self.incr()
        return node