import os
import sys
from typing import Callable

import papermill as pm
import scrapbook as sb

from pymbse.pymbse.model_api.executor.executor import Executor

MODEL_RESULTS_KEYWORD = 'model_results'


class ScriptExecutor(Executor):
    """ScriptExecutor class is implementing Executor abstract class and, particularly, the execute method for
    scripts obtained from notebooks.

    """

    def execute(self) -> dict:
        script = self.model_dependency_config.get_script_name_without_ext()
        cwd = os.getcwd()

        os.chdir(self.model_dependency_config.get_root_dir())

        # Unload a module to allow for its modification between subsequent calls
        if script in sys.modules.keys():
            sys.modules.pop(script)
        run = ScriptExecutor._import_function_from_module(script, 'run_' + script)
        fom_model = run(**self.input_parameters)
        os.chdir(cwd)

        return fom_model

    @staticmethod
    def _import_function_from_module(module: str, function: str) -> Callable:
        return getattr(__import__(module), function)


class NotebookExecutor(Executor):
    """NotebookExecutor class is implementing Executor abstract class and, particularly, the execute method for
    notebooks.

    """

    def execute(self) -> dict:
        model_out_abs_path = self.model_dependency_config.get_ipynb_out_abs_path()
        pm.execute_notebook(self.model_dependency_config.model_abs_path,
                            model_out_abs_path,
                            cwd=self.model_dependency_config.get_root_dir(),
                            parameters=self.input_parameters)

        return sb.read_notebook(model_out_abs_path).scraps[MODEL_RESULTS_KEYWORD].data
