import _collections_abc
import math


# Source: https://stackoverflow.com/questions/5194057/better-way-to-convert-file-sizes-in-python
def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class TrackedList(_collections_abc.MutableSequence):
    """ TrackedList is a wrapper for a list that will propagate changes to a Configuration. """

    def __init__(self, data, parent, attribute):
        self.data = []
        self._parent = parent
        self._parent_attr = attribute
        if data is not None:
            if type(data) == type(self.data):
                self.data[:] = data
            elif isinstance(data, TrackedList):
                self.data[:] = data.data[:]
            else:
                print(type(data))
                self.data = list(data)

        self.propagate()

    def __repr__(self):
        return repr(self.data)

    def __lt__(self, other):
        return self.data < self.__cast(other)

    def __le__(self, other):
        return self.data <= self.__cast(other)

    def __eq__(self, other):
        return self.data == self.__cast(other)

    def __gt__(self, other):
        return self.data > self.__cast(other)

    def __ge__(self, other):
        return self.data >= self.__cast(other)

    def __cast(self, other):
        return other.data if isinstance(other, TrackedList) else other

    def __contains__(self, item):
        return item in self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return self.__class__(self.data[i])
        else:
            return self.data[i]

    def __setitem__(self, i, item):
        self.data[i] = item
        self.propagate()


    def __delitem__(self, i):
        del self.data[i]
        self.propagate()


    def __add__(self, other):
        if isinstance(other, TrackedList):
            return self.__class__(self.data + other.data, self._parent, self._parent_attr)
        elif isinstance(other, type(self.data)):
            return self.__class__(self.data + other, self._parent, self._parent_attr)
        return self.__class__(self.data + list(other), self._parent, self._parent_attr)

    def __radd__(self, other):
        if isinstance(other, TrackedList):
            return self.__class__(other.data + self.data, self._parent, self._parent_attr)
        elif isinstance(other, type(self.data), self._parent, self._parent_attr):
            return self.__class__(other + self.data, self._parent, self._parent_attr)
        return self.__class__(list(other) + self.data, self._parent, self._parent_attr)

    def __iadd__(self, other):
        if isinstance(other, TrackedList):
            self.data += other.data
        elif isinstance(other, type(self.data)):
            self.data += other
        else:
            self.data += list(other)
        return self

    def __mul__(self, n):
        return self.__class__(self.data * n, self._parent, self._parent_attr)

    __rmul__ = __mul__

    def __imul__(self, n):
        self.data *= n
        return self

    def __copy__(self):
        inst = self.__class__.__new__(self.__class__)
        inst.__dict__.update(self.__dict__)
        # Create a copy and avoid triggering descriptors
        inst.__dict__["data"] = self.__dict__["data"][:]
        return inst

    def propagate(self):
        if self._parent:
            self._parent.propagate_to_parent(self._parent_attr, self.data)

    def append(self, item):
        self.data.append(item)
        self.propagate()

    def insert(self, i, item):
        self.data.insert(i, item)
        self.propagate()


    def pop(self, i=-1):
        p = self.data.pop(i)
        self.propagate()
        return p

    def remove(self, item):
        self.data.remove(item)
        self.propagate()


    def clear(self):
        self.data.clear()
        self.propagate()

    def copy(self):
        return self.__class__(self, self._parent, self._parent_attr)

    def count(self, item):
        return self.data.count(item)

    def index(self, item, *args):
        return self.data.index(item, *args)

    def reverse(self):
        self.data.reverse()

    def sort(self, /, *args, **kwds):
        self.data.sort(*args, **kwds)

    def extend(self, other):
        if isinstance(other, TrackedList):
            self.data.extend(other.data)
        else:
            self.data.extend(other)
