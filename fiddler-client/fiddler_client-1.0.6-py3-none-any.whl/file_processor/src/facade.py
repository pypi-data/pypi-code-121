from fiddler.file_processor.src.extractor import FileExtractor
from fiddler.file_processor.src.file_workflow_executor import (
    DatasetUploadWorkflowExecutor,
)
from fiddler.file_processor.src.processor import FileProcessorBase


def upload_dataset(files, source_data_source, file_type, schema=None):
    extractor = FileExtractor.get_extractor(source_data_source)
    processor = FileProcessorBase.get_processor(file_type, schema)
    executor = DatasetUploadWorkflowExecutor(extractor, processor)
    return executor.execute(files)
