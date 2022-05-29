import numpy as np
import pandas as pd
import wfsim
import straxen
import strax
import nestpy
import typing as ty
from strax.utils import tqdm
from warnings import warn

export, __all__ = strax.exporter()


@export
def rand_instructions(
        event_rate: int,
        chunk_size: int,
        n_chunk: int,
        drift_field: float,
        energy_range: ty.Union[tuple, list, np.ndarray],
        tpc_length: float = straxen.tpc_z,
        tpc_radius: float = straxen.tpc_r,
        nest_inst_types: ty.Union[ty.List[int], ty.Tuple[ty.List], np.ndarray, None] = None,
) -> dict:
    """
    Generate instructions to run WFSim
    :param event_rate: # events per second
    :param chunk_size: the size of each chunk
    :param n_chunk: the number of chunks
    :param energy_range: the energy range (in keV) of the recoil type
    :param tpc_length: the max depth of the detector
    :param tpc_radius: the max radius of the detector
    :param nest_inst_types: the
    :param drift_field:
    :return:
    """
    if nest_inst_types is None:
        nest_inst_types = [7]

    n_events = event_rate * chunk_size * n_chunk
    total_time = chunk_size * n_chunk

    inst = np.zeros(2 * n_events, dtype=wfsim.instruction_dtype)
    inst[:] = -1

    uniform_times = total_time * (np.arange(n_events) + 0.5) / n_events

    inst['time'] = np.repeat(uniform_times, 2) * int(1e9)
    inst['event_number'] = np.digitize(inst['time'],
                                       1e9 * np.arange(n_chunk) *
                                       chunk_size) - 1
    inst['type'] = np.tile([1, 2], n_events)

    r = np.sqrt(np.random.uniform(0, tpc_radius ** 2, n_events))
    t = np.random.uniform(-np.pi, np.pi, n_events)
    inst['x'] = np.repeat(r * np.cos(t), 2)
    inst['y'] = np.repeat(r * np.sin(t), 2)
    inst['z'] = np.repeat(np.random.uniform(-tpc_length, 0, n_events), 2)

    # Here we'll define our XENON-like detector
    nest_calc = nestpy.NESTcalc(nestpy.VDetector())
    nucleus_A = 131.293
    nucleus_Z = 54.
    lxe_density = 2.862  # g/cm^3   #SR1 Value

    energy = np.random.uniform(*energy_range, n_events)
    quanta = []
    exciton = []
    recoil = []
    e_dep = []
    for energy_deposit in tqdm(energy, desc='generating instructions from nest'):
        interaction_type = np.random.choice(nest_inst_types)
        interaction = nestpy.INTERACTION_TYPE(interaction_type)
        y = nest_calc.GetYields(interaction,
                                energy_deposit,
                                lxe_density,
                                drift_field,
                                nucleus_A,
                                nucleus_Z,
                                )
        q = nest_calc.GetQuanta(y, lxe_density)
        quanta.append(q.photons)
        quanta.append(q.electrons)
        exciton.append(q.excitons)
        exciton.append(0)
        # both S1 and S2
        recoil += [interaction_type, interaction_type]
        e_dep += [energy_deposit, energy_deposit]

    inst['amp'] = quanta
    inst['local_field'] = drift_field
    inst['n_excitons'] = exciton
    inst['recoil'] = recoil
    inst['e_dep'] = e_dep
    for field in inst.dtype.names:
        if np.any(inst[field] == -1):
            warn(f'{field} is not (fully) filled')
    return inst


@export
def inst_to_csv(csv_file: str,
                get_inst_from=rand_instructions,
                **kwargs):
    """
    Write instructions to csv file
    :param csv_file: path to the csv file
    :param get_inst_from: function to modify instructions and generate
    S1 S2 instructions from
    :param kwargs: key word arguments to give to the get_inst_from-function
    """
    df = pd.DataFrame(get_inst_from(**kwargs))
    if np.any(df['amp'] <= 0):
        warn('Removing zero amplitude from instruction, but that shouldn\'t be here')
        df = df[df['amp'] > 0]
    df.to_csv(csv_file, index=False)
