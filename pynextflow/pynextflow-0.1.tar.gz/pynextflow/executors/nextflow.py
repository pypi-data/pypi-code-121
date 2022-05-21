import sys
from io import StringIO

import os
import uuid
from datetime import datetime
from typing.io import TextIO

from pynextflow.entities.workflow import Workflow
from pynextflow.executors import Executor
from pynextflow.utils import _strip_indent, unpickle
from pynextflow.workflow import _print_workflow


class Nextflow(Executor):
    """
    Executor that runs locally using Nextflow (it must be available at the PATH).
    """

    def __init__(
            self,
            profile: str = None,
            name: str = None,
            workDir: str = None,
            debug: bool = False,
            clean: bool = True
    ):
        """
        Create a local executor using Nextflow

        @param clean: Do not remove generated Nextflow pipeline file
        @param debug: Instead of executing the pipeline returns the Nextflow generated code.
        """
        Executor.__init__(self)
        self.profile = profile
        self.name = name
        self.workDir = workDir
        self.debug = debug
        self.clean = clean

    def run(self, work: Workflow, returns=False):
        if self.debug:
            script = StringIO()
            self._write_nf_script(returns, "script.nf", work, script)
            return script.getvalue()

        return self._run(work, returns)

    def _run(self, work, returns):
        suffix_date = datetime.now().strftime("%Y%m%d_%H%M%s")
        suffix_rnd = str(uuid.uuid4())[0:8]
        basedir, script_name = os.getcwd(), f"pynextflow_{suffix_date}_{suffix_rnd}.nf"
        script_path = os.path.join(basedir, script_name)

        with open(script_path, "w") as fd:
            self._write_nf_script(returns, script_name, work, fd)

        options_str = self.command_options()
        command = f"cd {basedir} && NXF_ANSI_LOG=false nextflow run {script_name} {options_str}"
        try:
            exit_code = os.system(command)
            if exit_code != 0:
                raise RuntimeError(f"Nextflow ended with error code {exit_code}")

            if returns:
                # Unpickle returns
                return unpickle(f"returns/{script_name}.pkl")

            return None

        finally:
            if self.clean:
                os.remove(script_path)

    def command_options(self):
        # Build run options
        options = []
        if self.profile:
            options.append(f"-profile \"{self.profile}\"")
        if self.name:
            options.append(f"-name {self.name}")
        if self.workDir:
            options.append(f"-work-dir \"{self.workDir}\"")

        # Build run command
        options_str = " ".join(options)
        return options_str

    def _write_nf_script(self, returns: bool, scriptname: str, work: Workflow, fd: TextIO):
        _print_workflow(work, file=fd)
        if returns:
            print(self.results_process(scriptname), file=fd)

    @staticmethod
    def results_process(scriptname):
        return _strip_indent(f"""
                process _return_result {{
                    publishDir 'returns'
                
                    input:
                        path('results')
                
                    output:
                        path('{scriptname}.pkl')
                
                    script:
                    \"\"\"
                    /usr/bin/env python3 << EOF
                    
                    import pynextflow as nf
                    from glob import glob
                    nf.pickle([nf.unpickle(r) for r in glob("results*")], '{scriptname}.pkl')
                    
                    EOF
                    \"\"\"
                }}
                """)
