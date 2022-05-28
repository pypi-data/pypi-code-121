from __future__ import annotations

from bidict import bidict

from .vector import BoardVector


class BoardException(Exception):
    pass


class TileOccupiedException(BoardException):
    pass


class OutOfBoundsExcepion(BoardException):
    pass


class DuplicateObjectException(BoardException):
    pass


class HasOwnerException(BoardException):
    pass


class ObjectNotFound(BoardException):
    pass


class BoardObject:
    def __init__(self):
        self._board: Board | None = None

    @property
    def board(self):
        return self._board

    def get_pos(self) -> BoardVector:
        return self.board.get_object_pos(self)

    def move(self, transform: BoardVector):
        return self.board.move_object(self, transform)

    def _near(self, pos_iter):
        for pos in pos_iter:
            obj = self.board.get_object_at(pos)
            if obj is not None:
                yield pos, obj

    def adjacent(self):
        return self._near(self.get_pos().adjacent)

    def neighboring(self):
        return self._near(self.get_pos().neighboring)


class BoardValue(BoardObject):
    def __init__(self, val):
        super().__init__()

        self.value = val


class Board:
    def __init__(self, width, height):
        self._width = width
        self._height = height
        self._objects = bidict()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    def is_out_of_bounds(self, pos: BoardVector):
        return pos.x not in range(self.width) or pos.y not in range(self.height)

    def _check_out_of_bounds(self, pos: BoardVector):
        if self.is_out_of_bounds(pos):
            raise OutOfBoundsExcepion("Given position is out of bounds.")

    def remove_object(self, obj: BoardObject):
        obj._board = None
        del self._objects.inverse[obj]

    def remove_object_at(self, pos: BoardVector):
        self.remove_object(self._objects[pos])

    def get_object_at(self, pos: BoardVector):
        return self._objects.get(pos, None)

    def get_object_pos(self, obj: BoardObject):
        return self._objects.inverse.get(obj, None)

    def emplace_object(self, obj: BoardObject, pos: BoardVector, force_emplacement=False) -> bool:
        self._check_out_of_bounds(pos)

        if obj in self._objects.values():
            raise DuplicateObjectException("The same object can not be placed on a board twice.")

        if obj._board is not None:
            raise HasOwnerException("The given object is placed on another board.")

        if self.get_object_at(pos) is not None:
            if force_emplacement:
                self.remove_object_at(pos)
            else:
                return False

        obj._board = self
        self._objects[pos] = obj

        return True

    def emplace_value(self, val, pos: BoardVector) -> BoardValue:
        obj = BoardValue(val)
        self.emplace_object(obj, pos)
        return obj

    def move_object_to(self, obj: BoardObject, pos: BoardVector):
        if self.is_out_of_bounds(pos):
            return False

        if self.get_object_at(pos) is not None:
            return False

        self._objects.inverse[obj] = pos
        return True

    def move_object(self, obj: BoardObject, transform: BoardVector):
        return self.move_object_to(obj, self.get_object_pos(obj) + transform)

    def objects(self):
        for pos, obj in self._objects.items():
            yield pos, obj
