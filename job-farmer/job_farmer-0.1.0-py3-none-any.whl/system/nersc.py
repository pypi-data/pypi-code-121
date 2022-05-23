"""
File containing the system class for the NERSC systems.
"""
from .system import System
from typing import List


class CoriHaswell(System):
    """
    System class for the NERSC Cori-haswell system.
    Reference and documentation is available here:
     https://docs.nersc.gov/systems/cori/#system-specification
    """
    def __init__(self):
        """
        Constructor for the Cori-Haswell system
        """
        super().__init__(system_name='cori-haswell',
                         physical_cpu_cores_per_node=32,
                         threads_per_cpu_core=2,
                         physical_gpu_per_node=0,
                         memory_per_node_gb=128,
                         queues=['regular', 'shared', 'interactive', 'debug', 'premium', 'flex'])

    def get_constrains(self) -> List[str]:
        """
        System constraints for Cori-Haswell
        :return:
        """
        constrains = ['#SBATCH -C haswell']
        return constrains


class CoriKNL(System):
    """
    System class for the NERSC Cori-KNL system.
    Reference and documentation is available here:
     https://docs.nersc.gov/systems/cori/#system-specification
    """
    def __init__(self):
        """
        Constructor for the Cori-KNL system
        """
        super().__init__(system_name='cori-knl',
                         physical_cpu_cores_per_node=64,
                         threads_per_cpu_core=4,
                         physical_gpu_per_node=0,
                         memory_per_node_gb=96,
                         queues=['regular', 'interactive', 'debug', 'premium', 'low', 'flex'])

    def get_constrains(self) -> List[str]:
        """
        System constraints for Cori-KNL
        :return:
        """
        constrains = ['#SBATCH -C knl']
        return constrains


class PerlmutterCPU(System):
    """
    System class for the NERSC Perlmutter system.
    Reference and documentation is available here:
    https://docs.nersc.gov/systems/perlmutter/system_details/#system-specification-phase-1
    """
    def __init__(self):
        """
        Constructor for the Perlmutter CPU only system
        """
        super().__init__(system_name='perlmutter-cpu',
                         physical_cpu_cores_per_node=64,
                         threads_per_cpu_core=2,
                         physical_gpu_per_node=4,
                         memory_per_node_gb=256,
                         queues=['regular', 'interactive', 'debug'])

    def get_constrains(self) -> List[str]:
        """
        System constraints for Perlmutter.
        Documentation here:
        https://docs.nersc.gov/systems/perlmutter/running-jobs/#tips-and-tricks
        :return:
        """
        constrains = ['#SBATCH -C cpu']
        return constrains
