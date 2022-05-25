from typing import Type, List, Optional
from abc import ABC, abstractmethod, abstractclassmethod

from openlineage.airflow.extractors.base import TaskMetadata

from tokyo_lineage.models.base import BaseTask
from tokyo_lineage.utils.logging_mixin import LoggingMixin

class BaseMetadataExtractor(ABC, LoggingMixin):
    def __init__(self, task: Type[BaseTask]):
        self.task = task

    @abstractclassmethod
    def get_operator_classnames(cls) -> List[str]:
        pass
    
    def validate(self):
        assert (self.task.operator in self.get_operator_classnames())
    
    @abstractmethod
    def extract(self) -> Optional[TaskMetadata]:
        pass