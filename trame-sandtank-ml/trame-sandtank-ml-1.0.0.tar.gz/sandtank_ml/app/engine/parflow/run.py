r"""
ParFlow needs to be installed with $PARFLOW_DIR defined
"""
import numpy as np
import parflow
import tempfile, shutil
from trame.app import asynchronous

from .refs import copy_refs


def parflow_run(queue, left, right, time=10, run_directory=None, delete_on_exit=True):
    if run_directory is None:
        run_directory = tempfile.mkdtemp()

    with asynchronous.StateQueue(queue) as state:
        state.parflow_running = True

        # Run parflow
        copy_refs(run_directory)
        sandtank = parflow.Run.from_definition(f"{run_directory}/run.yaml")
        sandtank.Patch.x_lower.BCPressure.alltime.Value = left
        sandtank.Patch.x_upper.BCPressure.alltime.Value = right
        sandtank.dist("SandTank_Indicator.pfb")
        sandtank.run()

        # Extract results
        sandtank = parflow.Run.from_definition(f"{run_directory}/run.yaml")
        data = sandtank.data_accessor
        data.time = time
        (height, _, width) = data.shape

        # Update state
        state.parflow = {
            "size": (width, height),
            "bc": (left, right),
            "permeability": np.flipud(data.computed_permeability_x).flatten().tolist(),
            "pressure": np.flipud(data.pressure).flatten().tolist(),
            "saturation": np.flipud(data.saturation).flatten().tolist(),
            "ranges": {
                "pressure": [-30, 10],  # full range [-30, 50] => [-1, 1] |
                "saturation": [0, 1],
            },
            # "path": run_directory, # Just for debug
            "time": time,
        }

        state.parflow_running = False

    if delete_on_exit:
        shutil.rmtree(run_directory)
