import os
import tempfile

import numpy as np
import pyabc
import tidynamics

import fitmulticell as fmc


def test_cell_movement():
    """
    Just runs an analysis with the MAPK model to ensure that at least
    not execution errors occur.
    """
    file = os.path.normpath(os.getcwd() + os.sep)
    # file = os.getcwd()
    file_ = str(file + '/doc/example/models' + '/Demo_CellMotility.xml')
    par_map = {
        'motion_strength': './Global/Constant[@symbol="motion_strength"]',
        'noise_level': './Global/Constant[@symbol="noise_level"]',
    }
    model = fmc.model.MorpheusModel(
        file_,
        par_map=par_map,
        executable="morpheus",
        show_stdout=False,
        show_stderr=True,
        raise_on_error=False,
    )
    true_pars = {'motion_strength': 1.0, 'noise_level': 0.1}
    limits = {key: (0.1 * val, 10 * val) for key, val in true_pars.items()}
    measured_data = {
        'time': np.array([0, 100, 200, 300, 400]),
        'MSD': np.array([0, 1640, 5330, 10400, 15800]),
        'DAC': np.array([1, 0.49, 0.19, 0.07, 0.07]),
    }
    prior = pyabc.Distribution(
        **{
            key: pyabc.RV("uniform", lb, ub - lb)
            for key, (lb, ub) in limits.items()
        }
    )

    def distanceMSD(val1, val2):
        d = np.sum(
            np.abs(
                tidynamics.msd(
                    np.column_stack(
                        [
                            val1['cell.center.x'][1:],
                            val1['cell.center.y'][1:],
                        ]
                    )
                )
                - val2['MSD']
            )
        )
        return d

    def distanceDAC(val1, val2):
        d = np.sum(
            np.abs(
                tidynamics.acf(
                    np.column_stack(
                        [
                            val1['velocity.x'][1:]
                            / val1['velocity.abs'][1:],
                            val1['velocity.y'][1:]
                            / val1['velocity.abs'][1:],
                        ]
                    )
                )
                - val2['DAC']
            )
        )
        return d

    distance = pyabc.AggregatedDistance([distanceMSD, distanceDAC])
    abc = pyabc.ABCSMC(model, prior, distance, population_size=2)
    db_path = "sqlite:///" + os.path.join(tempfile.gettempdir(), "test.db")
    abc.new(db_path, measured_data)
    h = abc.run(max_nr_populations=2)
    assert h.n_populations == 2
