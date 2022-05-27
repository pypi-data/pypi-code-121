from typing import Callable, List

from torch import Tensor


class Compose:
    def __init__(self, transforms: List[Callable]) -> None:
        """Compose several transforms together.

        Each transform should be an instance of a class with a __call__ method.

        Args:
            transforms: the transforms to apply.
        """
        self.transforms = transforms

    def __call__(self, data: Tensor) -> Tensor:
        """Apply the transforms to the input data.

        Args:
            data: The data to transform.

        Returns:
            The transformed data.
        """
        for t in self.transforms:
            data = t(data)
        return data

    def __repr__(self) -> str:
        format_string = self.__class__.__name__ + "("
        for t in self.transforms:
            format_string += "\n"
            format_string += "    {0}".format(t)
            format_string += "\n)"
        return format_string
