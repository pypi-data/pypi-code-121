from mpi4py import MPI
import logging

from JuMonC.models import pluginInformation


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

logger = logging.getLogger(__name__)

def communicateAvaiablePlugins() -> None:
    findLocalPlugins()

def findLocalPlugins() -> None:
    test_papi()
    test_nv()
    test_linuxNet()
    test_cpu()
    test_mem()
    test_disk()
    
    
    # there are plugins like slurm that are only needed on the root node, therefore we only check for it there
    if rank == 0:
        test_slurm()


def test_papi() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks.Papi import PapiPlugin
    #pylint: enable=import-outside-toplevel
        
    plugin_p = PapiPlugin()
    pluginInformation.papi_is_working = bool(plugin_p.isWorking())
    if pluginInformation.papi_is_working is False:
        if rank == 0:
            logging.info("Could not load PAPI plugin")
        else:
            logging.debug("Could not load PAPI plugin")
            

def test_nv() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks import Nvidia
    #pylint: enable=import-outside-toplevel
        
    plugin_n = Nvidia.plugin
    pluginInformation.nvidia_is_working = bool(plugin_n.isWorking())
    if pluginInformation.nvidia_is_working is False:
        if rank == 0:
            logging.info("Could not load Nvidia plugin")
        else:
            logging.debug("Could not load Nvidia plugin")
            
            
def test_linuxNet() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks import LinuxNetwork
    #pylint: enable=import-outside-toplevel
        
    plugin_net = LinuxNetwork.plugin
    pluginInformation.network_is_working = bool(plugin_net.isWorking())
    if pluginInformation.network_is_working is False:
        if rank == 0:
            logging.info("Could not load Linux network plugin")
        else:
            logging.debug("Could not load Linux network plugin")


def test_cpu() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks import CPU
    #pylint: enable=import-outside-toplevel
        
    plugin_cpu = CPU.plugin
    pluginInformation.cpu_is_working = bool(plugin_cpu.isWorking())
    if pluginInformation.cpu_is_working is False:
        if rank == 0:
            logging.info("Could not load Linux CPU plugin")
        else:
            logging.debug("Could not load Linux CPU plugin")
    
def test_mem() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks import memory
    #pylint: enable=import-outside-toplevel
        
    plugin_mem = memory.plugin
    pluginInformation.memory_is_working = bool(plugin_mem.isWorking())
    if pluginInformation.memory_is_working is False:
        if rank == 0:
            logging.info("Could not load Linux memory plugin")
        else:
            logging.debug("Could not load Linux memory plugin")


def test_disk() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks import disk
    #pylint: enable=import-outside-toplevel
        
    plugin_disk = disk.plugin
    pluginInformation.disk_is_working = bool(plugin_disk.isWorking())
    if pluginInformation.disk_is_working is False:
        if rank == 0:
            logging.info("Could not load Linux disk plugin")
        else:
            logging.debug("Could not load Linux disk plugin")
    

def test_slurm() -> None:
    #pylint: disable=import-outside-toplevel
    from JuMonC.tasks.Slurm import SlurmPlugin
    #pylint: enable=import-outside-toplevel
            
    plugin_s = SlurmPlugin()
    pluginInformation.slurm_is_working = bool(plugin_s.isWorking())
    if pluginInformation.slurm_is_working is False:
        logging.info("Could not load Slurm plugin")