import os
from typing import Callable, Dict, Optional, Sequence
from pathlib import Path
from pipelime.converters.base import UnderfolderConverter
from pipelime.sequences.readers.base import ReaderTemplate
from pipelime.sequences.samples import FileSystemSample, SamplesSequence
from pipelime.sequences.writers.filesystem import UnderfolderWriterV2
import re


class Subfolders2Underfolder(UnderfolderConverter):
    def __init__(
        self,
        folder: str,
        images_extension: str = "png",
        use_symlinks: bool = False,
        num_workers: int = 0,
        progress_callback: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Converts a subfolder tree structure, containing images, to a single Underfolder.
        Subfolder structure should be like

        root
        - subfolder1
            - subfolder2
                - subfolder3
                    - image1.png
                    - image2.png
                - image3.png
            - image4.png

        Category for image2 will be 'subfolder1_subfolder2_subfolder3'. An so on...

        :param folder: root folder
        :type folder: str
        :param images_extension: image extension to include in conversion, defaults to "png"
        :type images_extension: str, optional
        :param use_symlinks: use symlinks instead of copying files, defaults to False
        :type use_symlinks: bool, optional
        :param num_workers: number of workers to use, defaults to 0
        :type num_workers: int, optional
        :param progress_callback: callback to report progress, defaults to None
        :type progress_callback: Optional[Callable[[dict], None]], optional
        """
        self._folder = folder
        self._use_symlinks = use_symlinks
        self._num_workers = num_workers
        self._progress_callback = progress_callback
        self._images_extension = images_extension

    def extensions_map(self) -> dict:
        return {
            "image": self._images_extension,
            "metadata": "yml",
            "classmap": "yml",
        }

    def root_files_keys(self) -> dict:
        return ["classmap"]

    def convert(self, output_folder: str):
        """

        :param output_folder: [description]
        :type output_folder: str
        """

        output_folder = Path(output_folder)
        if not output_folder.exists():
            output_folder.mkdir(parents=True, exist_ok=False)

        ic = self.extract_items_and_classmap(self._folder)

        samples = []
        for index, item in enumerate(ic["items"]):
            sample = FileSystemSample(data_map={}, id=index)
            sample.filesmap["image"] = item["filepath"]
            sample["metadata"] = {
                "category": item["category"],
                "filename": item["filename"],
            }
            sample["classmap"] = ic["classmap"]
            samples.append(sample)

        writer = UnderfolderWriterV2(
            folder=output_folder,
            file_handling=UnderfolderWriterV2.FileHandling.COPY_IF_NOT_CACHED,
            copy_mode=UnderfolderWriterV2.CopyMode.HARD_LINK,
            reader_template=ReaderTemplate(
                extensions_map=self.extensions_map(),
                root_files_keys=self.root_files_keys(),
            ),
            num_workers=self._num_workers,
            progress_callback=self._progress_callback,
        )
        writer(SamplesSequence(samples=samples))
