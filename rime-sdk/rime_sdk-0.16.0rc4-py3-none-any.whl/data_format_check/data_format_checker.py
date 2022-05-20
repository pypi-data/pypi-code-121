"""Shared types/logic for the data-specific checkers."""
from abc import abstractmethod
from pathlib import Path
from typing import Any, List


class DataFormatChecker:
    """Base class for the data-specific checkers."""

    success_msg = "\nYour data should work with RIME!\n"
    accepted_file_types: List[str]

    def check_file_format(self, file_path: Path) -> None:
        """Verify that the file at file_path is one of the accepted_file_types."""
        if file_path.suffix not in self.accepted_file_types:
            raise ValueError(
                "Invalid file format: '{}'. Input must be one of the "
                "following: {}".format(file_path, self.accepted_file_types)
            )

    @abstractmethod
    def check(self, ref_path: Path, eval_path: Path, task: str, **kwargs: Any) -> None:
        """Perform all checks necessary to validate given file(s).

        Main entry point.
        """
