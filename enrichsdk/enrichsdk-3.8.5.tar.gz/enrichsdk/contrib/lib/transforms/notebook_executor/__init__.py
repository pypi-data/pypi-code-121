import os
import json
from datetime import datetime, date, timedelta
from dateutil import parser as dateparser
import logging
import papermill as pm
from enrichsdk import Compute, S3Mixin, CheckpointMixin

logger = logging.getLogger("app")


class NotebookExecutorBase(Compute):
    """
    A built-in transform baseclass to handle standard notebook
    operation and reduce the duplication of code.

    Features of this transform include:

        * Support for custom args and environment
        * Support for automatic capture and surfacing of output and err

    Configuration looks like::

         class MyTestNotebook(NotebookExecutorBase):

             def __init__(self, *args, **kwargs):
                 super().__init__(*args, **kwargs)
                 self.name = "TestNotebook"
                 self.notebook = os.path.join(thisdir, "Test-Notebook.ipynb")

             @classmethod
             def instantiable(cls):
                 return True

             def get_environment(self):
                 return {
                     'SECRET': credentials
                 }
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = "NotebookExecutorBase"
        self.notebook = None
        self._environ = os.environ.copy()

    @classmethod
    def instantiable(cls):
        return False

    def preload_clean_args(self, args):
        """
        Standard args preprocessor. Make sure that
        an artifacts directory is created for storing the
        configuration file, output notebook and stdout/err.

        """
        args = super().preload_clean_args(args)

        # Insert artifacts if not available..
        if "artifacts" not in args:
            args["artifacts"] = self.get_file(
                "%(output)s/%(runid)s/artifacts", create_dir=True
            )
            try:
                os.makedirs(args["artifacts"])
            except:
                pass

        return args

    def get_notebook(self):
        """
        Define notebook that must be executed

        Returns:

            str: Path to the notebook
        """
        if (
            (not hasattr(self, "notebook"))
            or (self.notebook is None)
            or (not isinstance(self.notebook, str))
            or (not os.path.exists(self.notebook))
        ):
            raise Exception(
                "Missing notebook. Missing/invalid path: {}".format(
                    getattr(self, "notebook", "")
                )
            )

        notebook = self.notebook
        notebook = os.path.abspath(notebook)
        return notebook

    def get_environment(self):
        """
        Pass any additional parameters...
        """
        return {}

    def run_notebook(self, config, configfile):

        inputnb = self.get_notebook()
        name = os.path.basename(inputnb)
        outputnb = os.path.join(config["artifacts"], "run-" + name)

        # Pass whatever parameters that the notebook can accept
        params = {"config": configfile}

        outfile = os.path.join(config["artifacts"], name + ".out")
        errfile = os.path.join(config["artifacts"], name + ".err")

        try:
            pm.execute_notebook(
                inputnb,
                outputnb,
                parameters=params,
                progress_bar=False,
                log_output=True,
                stdout_file=open(outfile, "w"),
                stderr_file=open(errfile, "w"),
            )

            if not os.path.exists(outputnb):
                raise Exception("output notebook not generated")

            logger.debug(
                "Executed notebook: Stdout",
                extra={"transform": self.name, "data": open(outfile).read()},
            )
            logger.debug(
                "Executed notebook: Stderr",
                extra={"transform": self.name, "data": open(errfile).read()},
            )

        except:
            logger.exception(
                "Unable to run the notebook",
                extra={
                    "transform": self.name,
                },
            )
            raise

    def process(self, state):
        """
        Run the computation and update the state
        """
        logger.debug(
            "{} - process".format(self.name),
            extra=self.config.get_extra({"transform": self.name}),
        )

        config = self.args
        configfile = os.path.join(config["artifacts"], "config.json")
        dump = lambda: json.dumps(config, indent=4, default=str)
        with open(configfile, "w") as fd:
            fd.write(dump())

        logger.debug(
            "Parameters to script",
            extra={
                "transform": self.name,
                "data": "Config: {}\n---\n".format(configfile) + dump(),
            },
        )

        # Update the environ
        _environ = os.environ.copy()
        try:
            # Update the environ
            update = self.get_environment()
            os.environ.update(update)

            # Now run the notebook
            self.run_notebook(config, configfile)

        finally:
            os.environ.clear()
            os.environ.update(_environ)

        return state

    def validate_results(self, what, state):
        """
        Check to make sure that the execution completed correctly
        """
        pass
