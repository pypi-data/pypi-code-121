from abc import ABCMeta
from functools import partial
from typing import Mapping, Any

from ..control.model import RunResult
from ..service import DispatchTemplate, Command, CommandCollection, SectionInfoMapping, FileInput, \
    FileInputCollection, FileOutput, FileOutputCollection, Section, Task


class DispatchRunner(metaclass=ABCMeta):
    def __init__(self, template: DispatchTemplate):
        self.__template = template

    def _command_start(self, command: Command):
        pass

    def _command_complete(self, command: Command, result: RunResult):
        pass

    def _command_collection_start(self, collection: CommandCollection):
        pass

    def _command_collection_complete(self, collection: CommandCollection, result):
        pass

    def _info_mapping_start(self, mapping: SectionInfoMapping):
        pass

    def _info_mapping_complete(self, mapping: SectionInfoMapping, result):
        pass

    def _info_dump_start(self, section: Section, info: Mapping[str, Any]):
        pass

    def _info_dump_complete(self, section: Section, info: Mapping[str, Any]):
        pass

    def _input_start(self, input_: FileInput):
        pass

    def _input_complete(self, input_: FileInput):
        pass

    def _input_collection_start(self, collection: FileInputCollection):
        pass

    def _input_collection_complete(self, collection: FileInputCollection):
        pass

    def _output_start(self, output: FileOutput):
        pass

    def _output_complete(self, output: FileOutput):
        pass

    def _output_collection_start(self, collection: FileOutputCollection):
        pass

    def _output_collection_complete(self, collection: FileOutputCollection):
        pass

    def _section_start(self, section: Section):
        pass

    def _section_complete(self, section: Section, result):
        pass

    def _task_start(self, task: Task):
        pass

    def _task_complete(self, task: Task, result):
        pass

    def __call__(self, scriptdir: str, environ=None, environ_after=None, **kwargs):
        return partial(self.__template(
            scriptdir=scriptdir,
            environ=environ,
            environ_after=environ_after,
        ),
            command_start=self._command_start,
            command_complete=self._command_complete,
            command_collection_start=self._command_collection_start,
            command_collection_complete=self._command_collection_complete,
            info_mapping_start=self._info_mapping_start,
            info_mapping_complete=self._info_mapping_complete,
            info_dump_start=self._info_dump_start,
            info_dump_complete=self._info_dump_complete,
            input_start=self._input_start,
            input_complete=self._input_complete,
            input_collection_start=self._input_collection_start,
            input_collection_complete=self._input_collection_complete,
            output_start=self._output_start,
            output_complete=self._output_complete,
            output_collection_start=self._output_collection_start,
            output_collection_complete=self._output_collection_complete,
            section_start=self._section_start,
            section_complete=self._section_complete,
            task_start=self._task_start,
            task_complete=self._task_complete,
            **kwargs
        )
