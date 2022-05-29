import pema
import straxen
import wfsim

_input_dict = dict(
    event_rate=20,  # Don't make too large -> overlapping truth info
    chunk_size=5,  # keep large -> less overhead but takes more RAM
    n_chunk=10,
    tpc_radius=straxen.tpc_r,
    tpc_length=straxen.tpc_z,
    drift_field=10,  # kV/cm
    energy_range=[1, 10],  # keV
    nest_inst_types=wfsim.NestId.ER,
)


def test_rand_instructions():
    pema.rand_instructions(**_input_dict)
