import os
import datetime
from abc import abstractmethod, ABC
from typing import Union

from pydantic import BaseModel

from pymbse.pymbse.config.notebook_script_config import ScriptConfig
from pymbse.pymbse.model_api.snapshot.model_snapshot import ModelSnapshot
from pymbse.commons import text_file
from pymbse.pymbse.config.pymbse_config import NotebookScriptConfig


FIGURES_OF_MERIT_KEYWORD = 'fom'
ARTEFACTS_KEYWORD = 'artefacts'


class Executor(BaseModel, ABC):
    """Abstract dataclass storing a model dependency config container and parameters dictionary needed for model
    execution. The execute method is abstract and implemented per each subclass.

    """
    model_dependency_config: Union[ScriptConfig, NotebookScriptConfig]
    input_parameters: dict

    @abstractmethod
    def execute(self) -> dict:
        """Method executing a model (e.g., a notebook, a scripted notebook) and returning a dictionary with figures of
        merit and artifact files

        :return: a dictionary with figures of merit and artefacts keywords mapping to dictionaries containing inforation
        for each of them
        """

    def execute_with_snapshot(self) -> ModelSnapshot:
        """Method executing a model and returning a model snapshot

        :return: an initialized ModelSnapshot instance
        """
        outputs_dct = self.execute()
        return self._initialize_model_snapshot(outputs_dct)

    def _initialize_model_snapshot(self,
                                   outputs_dct: dict) -> ModelSnapshot:
        """Method initializing a model snapshot from model execution output dictionary and additional pieces of
        information.

        :param outputs_dct: a dictionary with figures of merit and artefacts
        :return: an initialized ModelSnapshot instance
        """
        artefacts = read_artefacts(outputs_dct, self.model_dependency_config.get_root_dir())
        figures_of_merit = read_figures_of_merit(outputs_dct)
        return ModelSnapshot(name=self.model_dependency_config.get_model_name_without_ext(),
                             abs_path=self.model_dependency_config.model_abs_path,
                             execution_time=str(datetime.datetime.now()),
                             modification_timestamp=int(os.path.getmtime(self.model_dependency_config.model_abs_path)),
                             input_parameters=self.input_parameters,
                             artefacts=artefacts,
                             figures_of_merit=figures_of_merit)


def read_artefacts(outputs_dct: dict, model_dir: str) -> dict:
    """Function reading dictionaries and returning a dictionary. The dictionary is mapping from artefact name to its
    text content

    :param outputs_dct: a dictionary with figures of merit and artefacts
    :param model_dir: a root directory of a model
    :return: an empty dictionary if the artefact key is missing, otherwise a dictionary with artefact contents
    """
    if ARTEFACTS_KEYWORD not in outputs_dct:
        return {}

    return {artefact: read_artefact_as_text(model_dir, outputs_dct[ARTEFACTS_KEYWORD][artefact])
            for artefact in outputs_dct[ARTEFACTS_KEYWORD]}


def read_figures_of_merit(outputs_dct: dict) -> dict:
    """Function reading a dictionary with figures of merit from the output dictionary

    :param outputs_dct: a dictionary with figures of merit and artefacts
    :return: an empty dictionary if the figure of merit key is missing, otherwise a dictionary with figures of merit
    """
    if FIGURES_OF_MERIT_KEYWORD not in outputs_dct:
        return {}

    return outputs_dct[FIGURES_OF_MERIT_KEYWORD]


def read_artefact_as_text(root_dir: str, artefact_rel_path: str) -> str:
    """Function reading an artefact file as text. The artefact path is constructed from the root directory and the
    relative artefact path.

    :param root_dir: root directory
    :param artefact_rel_path: relative artefact path w.r.t. the root directory
    :return: a string with artefact file content
    """
    artefact_abs_path = os.path.join(root_dir, artefact_rel_path)
    return text_file.read(artefact_abs_path)
