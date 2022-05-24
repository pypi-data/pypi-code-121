from pathlib import Path
from typing import Callable, List, Tuple, cast

import torch
from torch import Tensor
from torch.utils.data import Dataset

from pycarus.transforms.var import Compose

T_ITEM = Tuple[str, str, Tensor, Tensor]


class Pcn(Dataset):
    """Class implementing the Point Completion Network dataset as proposed in:

    Yuan, W., Khot, T., Held, D., Mertz, C., & Hebert, M. (2018, September).
    Pcn: Point completion network.
    In 2018 International Conference on 3D Vision (3DV) (pp. 728-737). IEEE.
    """

    def __init__(
        self,
        root: Path,
        split: str,
        use_original_incomplete: bool = False,
        use_original_complete: bool = True,
        transforms_incomplete: List[Callable] = [],
        transforms_complete: List[Callable] = [],
        transforms_all: List[Callable] = [],
    ) -> None:
        """Create an instance of PCN dataset.

        Args:
            root: The path to the root directory of the dataset.
            split: The split to use (only "train", "val" and "test" allowed).
            use_original_incomplete: If True, use original incomplete clouds, which have
                a different number of points for each item. Otherwise, use incomplete clouds
                sampled with FPS to obtain 2048 points. Defaults to False.
            use_original_complete: If True, use original complete clouds, which have
                16384 points for each item. Otherwise, use complete clouds sampled with
                FPS to obtain 2048 points. Defaults to True.
            transforms_incomplete: The list of transforms to apply to incomplete pcds. Defaults to [].
            transforms_complete: The list of transforms to apply to complete pcds. Defaults to [].
            transforms_all: The list of transforms to apply to all pcds. Defaults to [].
        """
        super().__init__()

        assert split in ["train", "val", "test"]

        self.root = root / split
        self.num_items = len(list(self.root.glob("*.pt")))

        self.use_original_incomplete = use_original_incomplete
        self.use_original_complete = use_original_complete

        self.transform_complete = Compose(transforms_complete)
        self.transform_incomplete = Compose(transforms_incomplete)
        self.transform_all = Compose(transforms_all)

    def __len__(self) -> int:
        """Return the number of items in the dataset.

        Returns:
            The number of items in the dataset.
        """
        return self.num_items

    def __getitem__(self, index: int) -> T_ITEM:
        """Return the item at the given index.

        The number of points of incomplete and complete clouds depends on the
        flags "use_original_incomplete" and "use_original_complete" set when
        creating the dataset.

        Args:
            index: The index of the required item.

        Returns:
            - The category of the item.
            - The name of the item.
            - A tensor with the incomplete point cloud with shape (NUM_POINTS, 3).
            - A tensor with the complete point cloud with shape (NUM_POINTS, 3).
        """
        item_path = self.root / f"{index}.pt"
        item = torch.load(item_path)  # type: ignore

        category = cast(str, item["category"])
        name = cast(str, item["name"])

        if self.use_original_incomplete:
            incomplete = cast(Tensor, item["original_incomplete"])
        else:
            incomplete = cast(Tensor, item["incomplete_fps"])

        if self.use_original_complete:
            complete = cast(Tensor, item["original_complete"])
        else:
            complete = cast(Tensor, item["complete_fps"])

        incomplete = self.transform_all(self.transform_incomplete(incomplete))
        complete = self.transform_all(self.transform_complete(complete))

        return category, name, incomplete, complete
