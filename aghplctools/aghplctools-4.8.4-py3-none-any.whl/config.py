"""
Common configuration variables which are consistent across the system
"""
import warnings
from typing import List
from .local_paths import ChemStationConfig, AcquisitionSearch

warnings.warn(  # v4.5.0
    'the config module has been deprecated, import from local_paths and adjust your code away from the variable retrieval',
    DeprecationWarning,
    stacklevel=2,
)

ChemStationConfig.construct_from_ini()
ChemStationConfig.construct_from_env()

AcquisitionSearch.start_monitoring_all_paths()

# legacy value retrieval
CHEMSTATION_CORE_PATH = ChemStationConfig.registered_chemstations[0].core_path if len(ChemStationConfig.registered_chemstations) > 0 else None
CHEMSTATION_DATA_PATHS = [
    inst.data_path.data_parent
    for inst in ChemStationConfig.registered_chemstations
]
CHEMSTATION_DATA_PATH = CHEMSTATION_DATA_PATHS[0] if len(CHEMSTATION_DATA_PATHS) > 0 else None
CHEMSTATION_VERSION = ChemStationConfig.registered_chemstations[0].version if len(ChemStationConfig.registered_chemstations) > 0 else None
CHEMSTATION_METHOD_PATH = ChemStationConfig.registered_chemstations[0].method_path if len(ChemStationConfig.registered_chemstations) > 0 else None

# automatically instantiate defined data paths
acquiring_monitors: List[AcquisitionSearch] = AcquisitionSearch.instances
