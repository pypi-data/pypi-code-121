# jagonzal: MPIServer initialization before watchdog fork
from casampi.MPIEnvironment import MPIEnvironment

if MPIEnvironment.is_mpi_enabled and not MPIEnvironment.is_mpi_client:
    from . import server_run
    server_run.run()
    # Servers make sure to exit here
    # raise SystemExit(0) would be the right thing to do, gut that doesn't go well with
    # casashell -c. Casashell would after this go on to the next steps in its sequence of
    # init/load scripts and do for example init_welcome. The MPI servers need to exit now
    # raise SystemExit(0)
    import os
    os._exit(0)

# jagonzal: MPIClient initialization, alternative to server / after watchdog fork
if MPIEnvironment.is_mpi_enabled and MPIEnvironment.is_mpi_client:
    # Instantiate MPICommunicator singleton in order not to block the clients
    from .MPICommunicator import MPICommunicator
    mpi_comunicator = MPICommunicator()    
    # Post MPI related info
    from casatools import logsink
    casalog = logsink()
    casalog.post(MPIEnvironment.mpi_info_msg,"INFO","casa" )
