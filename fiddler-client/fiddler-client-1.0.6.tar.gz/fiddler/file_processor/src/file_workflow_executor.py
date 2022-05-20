from abc import ABC, abstractmethod
from dataclasses import dataclass

from fiddler.file_processor.src.extractor import FileExtractor
from fiddler.file_processor.src.processor import FileProcessorBase


class WorkflowExecutor(ABC):
    @abstractmethod
    def execute(self, files):
        pass


@dataclass
class DatasetUploadWorkflowExecutor(WorkflowExecutor):
    extractor: FileExtractor
    processor: FileProcessorBase

    def execute(self, files):
        files_list = self.extractor.extract(files)
        return self.processor.process(files_list)
