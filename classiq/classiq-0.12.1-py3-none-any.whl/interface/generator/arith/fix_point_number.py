from __future__ import annotations

import math
from typing import List, Optional, Union, overload

import pydantic
from typing_extensions import Literal

from classiq.interface.generator.arith.register_user_input import RegisterUserInput

MAX_FRACTION_PLACES = 5
BitString = Literal["0", "1"]


# TODO This class is fundamentally broken, as it's __iter__ function disagrees with its __len__ and __getitem__
# functions. As a result, both of those code snippets do different things:
# - list(fixed_point_number)  # Iterates over fields
# - [fixed_point_number[i] for i in range(len(fixed_point_number))]  # Iterates over bits


class FixPointNumber(pydantic.BaseModel):
    float_value: float
    max_fraction_places: int = MAX_FRACTION_PLACES
    _is_signed: bool = pydantic.PrivateAttr(default=False)
    _fraction_places: int = pydantic.PrivateAttr(default=0)
    _int_val: int = pydantic.PrivateAttr(default=0)
    _size: pydantic.PositiveInt = pydantic.PrivateAttr(default=1)
    _integer_part_size: pydantic.PositiveInt = pydantic.PrivateAttr(default=1)
    _is_initiated: bool = pydantic.PrivateAttr(default=False)

    def _initiate_values(self) -> None:
        if self.float_value < 0.0:
            self._is_signed = True
        self.set_int_representation()
        self._size = max(
            self.bit_length(should_ensure_initiation=False), self._fraction_places
        )
        self._integer_part_size = self._size - self._fraction_places
        self._is_initiated = True

    def set_int_representation(self) -> None:
        int_val = int(self.float_value * 2**self.max_fraction_places)
        int_val = self.signed_int_to_unsigned(int_val)

        if int_val == 0:
            fraction_places = 0
        else:
            bin_val = bin(int_val)[2:]
            fraction_places = self.max_fraction_places
            for b in reversed(bin_val):
                if b == "1" or fraction_places == 0:
                    break
                fraction_places -= 1
            int_val = int_val >> (self.max_fraction_places - fraction_places)

        self._fraction_places = fraction_places
        self._int_val = int_val

    @staticmethod
    def signed_int_to_unsigned(number: int):
        """Return the integer value of a signed int if it would we read as un-signed in binary representation"""
        if number >= 0:
            return number

        not_power2 = abs(number) & (abs(number) - 1) != 0
        return number + 2 ** (number.bit_length() + 1 * not_power2)

    @staticmethod
    def binary_to_float(bin_rep: str, fraction_part_size: int, is_signed: bool = False):
        negative_offset = -(2 ** len(bin_rep)) * (bin_rep[0] == "1") * is_signed
        value = int(bin_rep, 2) + negative_offset
        if (
            fraction_part_size > 0
        ):  # separated the clause to so that the value remains int if there is no fraction part
            value = value / 2**fraction_part_size
        return value

    @property
    def is_signed(self) -> bool:
        if not self._is_initiated:
            self._initiate_values()
        return self._is_signed

    @property
    def fraction_places(self):
        if not self._is_initiated:
            self._initiate_values()
        return self._fraction_places

    def set_fraction_places(self, value: int):
        if value < self._fraction_places and self.int_val != 0:
            raise ValueError("size cannot be lower than minimum number bits required")

        if value > self.max_fraction_places:
            self.max_fraction_places = value
            self._initiate_values()

        self._int_val = math.floor(self.int_val * 2 ** (value - self.fraction_places))
        self._fraction_places = value
        self._size = self._integer_part_size + self._fraction_places

    @property
    def int_val(self):
        if not self._is_initiated:
            self._initiate_values()
        return self._int_val

    @property
    def integer_part_size(self):
        if not self._is_initiated:
            self._initiate_values()
        return self._integer_part_size

    def set_integer_part_size(self, value: int):
        if value < self.integer_part_size and self.int_val != 0:
            raise ValueError("size cannot be lower than minimum number bits required")
        self._integer_part_size = value
        self._size = self._integer_part_size + self._fraction_places
        self._int_val = int(self.bin_val, 2)

    def bit_length(self, *, should_ensure_initiation=True) -> pydantic.PositiveInt:
        if should_ensure_initiation and not self._is_initiated:
            self._initiate_values()
        return 1 if self._int_val == 0 else self._int_val.bit_length()

    @property
    def size(self):
        if not self._is_initiated:
            self._initiate_values()
        return self._size

    def __len__(self):
        return self.size

    @property
    def bin_val(self) -> str:
        if not self._is_initiated:
            self._initiate_values()

        bin_rep = bin(self._int_val)[2:]
        size_diff = self.size - len(bin_rep)
        if self.float_value >= 0:
            return "0" * size_diff + bin_rep
        else:
            return "1" * size_diff + bin_rep

    @property
    def actual_float_value(self):
        return self.binary_to_float(self.bin_val, self.fraction_places, self._is_signed)

    @property
    def bounds(self):
        value = self.actual_float_value
        return value, value

    def to_register_user_input(
        self, *, name: Optional[str] = None
    ) -> RegisterUserInput:
        return RegisterUserInput(
            name=name,
            size=self.size,
            is_signed=self.is_signed,
            fraction_places=self.fraction_places,
        )

    def __eq__(self, other):
        return self.actual_float_value == other

    def __ge__(self, other):
        return self.actual_float_value >= other

    def __gt__(self, other):
        return self.actual_float_value > other

    def __le__(self, other):
        return self.actual_float_value <= other

    def __lt__(self, other):
        return self.actual_float_value < other

    def __ne__(self, other):
        return self.actual_float_value != other

    @overload
    def __getitem__(self, item: int) -> BitString:
        ...

    @overload
    def __getitem__(self, item: slice) -> List[BitString]:
        ...

    def __getitem__(self, item: Union[slice, int]) -> Union[List[BitString], BitString]:
        return [v for v in self.bin_val[::-1]][  # type: ignore[return-value]
            item
        ]  # follow qiskit convention that LSB is the top wire, bigendian

    def __neg__(self):
        return FixPointNumber(
            float_value=-self.float_value, max_fraction_places=self.max_fraction_places
        )

    class Config:
        extra = "forbid"
