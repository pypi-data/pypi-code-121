from pymbse.pymbse.config.model_type import ModelType
from pymbse.pymbse.model_api.notebook_script_api import NotebookModelAPI, ScriptModelAPI, NotebookScriptModelAPI

model_type_to_api = {ModelType.NOTEBOOK: NotebookModelAPI,
                     ModelType.SCRIPT: ScriptModelAPI,
                     ModelType.NOTEBOOK_SCRIPT: NotebookScriptModelAPI}