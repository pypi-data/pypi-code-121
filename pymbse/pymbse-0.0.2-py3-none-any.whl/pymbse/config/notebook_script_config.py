import os
from pathlib import Path
from typing import Set, List

import pydantic
from pydantic import BaseModel

from pymbse.pymbse.config.model_type import ModelType
from pymbse.pymbse.config.hash_functions import hash_file, hash_dict


class ModelMetadataForHash(BaseModel):
    """Class providing a container to store notebook metadata

    """
    model_file_hash: str
    input_file_to_hash: dict

    def upcast_to_root(self,
                       input_parameters: dict,
                       model_dependency_order_to_hash: dict
                       ) -> "RootModelMetadataForHash":
        return RootModelMetadataForHash(**self.dict(),
                                        input_parameters=input_parameters,
                                        model_dependency_order_to_hash=model_dependency_order_to_hash)


class RootModelMetadataForHash(ModelMetadataForHash):
    """Class providing a container to store model notebook metadata. It enhances the NotebookMetadata class with a
    dictionary of input parameters and a dictionary with model dependency hashes

    """
    input_parameters: dict
    model_dependency_order_to_hash: dict


class ScriptConfig(BaseModel):
    """Class storing script model config

    """
    model_abs_path: str
    model_type: ModelType
    input_files: Set[str]
    needs: List[str]

    class Config:
        use_enum_values = True

    @pydantic.validator('model_type', pre=True)
    def validate_enum_field(cls, model_type: str):
        return ModelType(model_type)

    def get_root_dir(self) -> str:
        """Method returning the root directory of a model

            >>> from pymbse.pymbse.config.notebook_script_config import ScriptConfig
            >>> config = ScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.py', model_type=ModelType.SCRIPT,
            >>> input_files=set(), needs=[])
            >>> config.get_root_dir()
            "C:\\magnetic"


        :return: string with the root directory of a model
        """
        return os.path.dirname(self.model_abs_path)

    def get_model_name_without_ext(self) -> str:
        """Method returning the model name without extension

            >>> from pymbse.pymbse.config.notebook_script_config import ScriptConfig
            >>> config = ScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.py', model_type=ModelType.SCRIPT,
            >>> input_files=set(), needs=[])
            >>> config.get_model_name_without_ext()
            "ROXIE"

        :return: string with model name without extension
        """
        return Path(self.model_abs_path).stem

    def get_script_name(self) -> str:
        """Method returning the script name for a notebook

            >>> from pymbse.pymbse.config.notebook_script_config import ScriptConfig
            >>> config = ScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.py', model_type=ModelType.SCRIPT,
            >>> input_files=set(), needs=[])
            >>> config.get_script_name()
            "ROXIE.py"

        :return: string with script name
        """
        _, path_tail = os.path.split(self.model_abs_path)
        return path_tail

    def get_script_name_without_ext(self) -> str:
        """Method returning the script name for a notebook without extension

            >>> from pymbse.pymbse.config.notebook_script_config import ScriptConfig
            >>> config = ScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.py',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_script_name_without_ext()
            "ROXIE"

        :return: string with script name
        """
        return self.get_model_name_without_ext()

    def get_script_abs_path(self) -> str:
        """Method returning the absolute path of a script name for a notebook

            >>> from pymbse.pymbse.config.notebook_script_config import ScriptConfig
            >>> from pymbse.pymbse.config.model_type import ModelType
            >>> config = ScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.py',
            >>> model_type=ModelType.SCRIPT, input_files=set(), needs=[])
            >>> config.get_script_abs_path()
            "C:\\magnetic\\ROXIE.py"

        :return: string with absolute path of script
        """
        return self.model_abs_path

    def create_input_file_to_hash_dict(self) -> dict:
        """Method creating a dictionary with hashed inputs. The dictionary is mapping from input name to content hash

        :return: a dictionary mapping from input file name to its content hash
        """
        current_model_root_dir = self.get_root_dir()
        input_file_to_hash = {}
        for input_file in self.input_files:
            input_file_path = (Path(current_model_root_dir) / Path(input_file)).resolve()
            input_file_to_hash[input_file] = hash_file(input_file_path)

        return input_file_to_hash

    def hash_model_metadata(self) -> str:
        return hash_dict(self.create_model_metadata().dict())

    def create_model_metadata(self) -> ModelMetadataForHash:
        input_file_to_hash = self.create_input_file_to_hash_dict()
        return ModelMetadataForHash(model_file_hash=hash_file(self.model_abs_path),
                                    input_file_to_hash=input_file_to_hash)


class NotebookScriptConfig(ScriptConfig):
    """Class storing notebook/script model config

    """

    def get_script_name(self) -> str:
        """Method returning the script name for a notebook

            >>> from pymbse.pymbse.config.notebook_script_config import NotebookScriptConfig
            >>> from pymbse.pymbse.config.model_type import ModelType
            >>> config = NotebookScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.ipynb',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_script_name()
            "ROXIE_script.py"

        :return: string with script name
        """
        script_name_without_ext = self.get_script_name_without_ext()
        return "%s.py" % script_name_without_ext

    def get_script_name_without_ext(self) -> str:
        """Method returning the script name for a notebook without extension

            >>> from pymbse.pymbse.config.notebook_script_config import NotebookScriptConfig
            >>> config = NotebookScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.ipynb',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_script_name_without_ext()
            "ROXIE_script"

        :return: string with script name
        """
        model_name = self.get_model_name_without_ext()
        return "%s_script" % model_name

    def get_script_abs_path(self) -> str:
        """Method returning the absolute path of a script name for a notebook

            >>> from pymbse.pymbse.config.notebook_script_config import NotebookScriptConfig
            >>> config = NotebookScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.ipynb',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_script_abs_path()
            "C:\\magnetic\\ROXIE_script.py"

        :return: string with absolute path of script
        """
        root_dir = self.get_root_dir()
        script_name = self.get_script_name()
        return os.path.join(root_dir, script_name).replace('\\', '/')

    def get_html_out_abs_path(self) -> str:
        """Method returning the absolute path of an HTML report

            >>> from pymbse.pymbse.config.notebook_script_config import NotebookScriptConfig
            >>> config = NotebookScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.ipynb',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_html_out_abs_path()
            "C:\\magnetic\\ROXIE_out.html"

        :return: string with absolute path of HTML report
        """
        root_dir = self.get_root_dir()
        model_name = self.get_model_name_without_ext()
        html_name = "%s_out.html" % model_name
        return os.path.join(root_dir, html_name).replace('\\', '/')

    def get_ipynb_out_abs_path(self) -> str:
        """Method returning the absolute path of an ipynb report

            >>> from pymbse.pymbse.config.notebook_script_config import NotebookScriptConfig
            >>> config = NotebookScriptConfig(model_abs_path='C:\\magnetic\\ROXIE.ipynb',
            >>> model_type=ModelType.NOTEBOOK_SCRIPT, input_files=set(), needs=[])
            >>> config.get_ipynb_out_abs_path()
            "C:\\magnetic\\ROXIE_out.ipynb"

        :return: string with absolute path of ipynb report
        """
        root_dir = self.get_root_dir()
        model_name = self.get_model_name_without_ext()
        ipynb_name = "%s_out.ipynb" % model_name
        return os.path.join(root_dir, ipynb_name).replace('\\', '/')
