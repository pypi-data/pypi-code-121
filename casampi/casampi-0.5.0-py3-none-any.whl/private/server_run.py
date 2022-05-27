#!/usr/bin/env python
from __future__ import absolute_import
from __future__ import print_function
import os 
import sys
import time
import signal

# The name of this file in mpi4py/casampi reflects that it was originally meant to take
# the place of 'casapy' in MPI mode in the server processes. A better name for the future
# could be server_init_run, server_run or similar

def is_fork_needed():
    """ With casampi (CASA 6) the exit handlers have changed. The fork/watchdog is
    not needed and actually causes trouble at interpreter shutdown time when exiting
    using a normal SystemExit. """
    fork_needed = True
    try:
        import casampi
        fork_needed = False
    except ImportError as exc:
        pass

    return fork_needed

# Create a watchdog to kill all processes in the group on exit
# as it seems that OpenMPI 1.10.2 only kills the main process
# but waits until all processes in the group finish
#
# Notice that it is not necessary to finalize MPI in the watchdog
# because it is not initialize either (MPI initialization happens
# when mpi4py is imported for the first time in MPIEnvironment)
if is_fork_needed() and os.fork( ) == 0 :
    
    # Install signal handlers
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    
    # Close standard input to avoid terminal interrupts
    sys.stdin.close( )
    sys.stdout.close( )
    sys.stderr.close( )
    os.close(0)
    os.close(1)
    os.close(2)

    # Check that parent process is alive
    ppid = os.getppid( )
    while True :
        try:
            os.kill(ppid,0)
        except:
            break
        time.sleep(3)

    # Kill process group
    os.killpg(ppid, signal.SIGTERM)
    sys.exit(1)
        
# CASA dictionary must be initialized here so that it can be found by stack inspection
casa = {}


# Use a function rather than import because with imports the Python import lock 
# is acquired by the main thread (this context) and other threads cannot import
def run():
    
    # Set CASA_ENGINGE env. variable so that:
    # - taskinit does not initialize the viewer
    # - taskmanmager is not initialized
    os.environ['CASA_ENGINE']="YES"

    # Initialize MPI environment
    from casampi.MPIEnvironment import MPIEnvironment

    # Initialize MPICommunicator singleton
    from .MPICommunicator import MPICommunicator
    communicator = MPICommunicator()

    # Wait to receive start service signal from MPI client processor
    start_service_signal_available = False
    while not start_service_signal_available:
        start_service_signal_available = communicator.control_service_request_probe()
        if start_service_signal_available:
            # Receive CASA global dictionary (filtered)
            request = communicator.control_service_request_recv()
        else:
            time.sleep(MPIEnvironment.mpi_start_service_sleep_time)

    # Check if request is start or stop signal
    if request['signal'] == 'start':

        cli_logfile_name, logmode_name = 'casa_filtered', 'logmode'
        for entry_name in [cli_logfile_name, logmode_name]:
            if entry_name not in request:
                raise RuntimeError('A \'start\' MPI request must have a {0} entry but it '
                                   'was not found. Host name: {1}. MPI rank: {2}, '.
                                   format(entry_name, MPIEnvironment.hostname,
                                          MPIEnvironment.mpi_processor_rank))

        # Get CASA environment dictionary
        global casa
        casa_filtered = request['casa_filtered']
        casa.update(casa_filtered)
        global _casa_top_frame_
        _casa_top_frame_ = True

        
        # Re-set log file
        if request[logmode_name] == 'separated' or request[logmode_name] == 'redirect':
            if 'files' in casa:
                casa['files']['logfile'] = ('{0}-server-{1}-host-{2}-pid-{3}'.
                                            format(casa['files']['logfile'],
                                                   MPIEnvironment.mpi_processor_rank,
                                                   MPIEnvironment.hostname,
                                                   MPIEnvironment.mpi_pid))
            try:
                casalog = logsink()
                logsing().setlogfile('{0}-server-{1}-host-{2}-pid-{3}'.
                                     format(casa['files']['logfile'],
                                            MPIEnvironment.mpi_processor_rank,
                                            MPIEnvironment.hostname,
                                            MPIEnvironment.mpi_pid))
            except Exception:
                pass

        # Import logger, logfile is set at taskinit retrieving from the casa dict. from the stack
        try:
            # CASA 6
            from casatools import logsink
            casalog = logsink()
        except ImportError:
            from taskinit import casalog

        from . import MPICommandServer as MPICS

        # Set log origin so that the processor origin is updated
        casalog_call_origin = "server_run"
        casalog.setglobal(True)
        casalog.origin(casalog_call_origin)

        # If log mode is separated activate showconsole to have all logs sorted by time at the terminal
        if request[logmode_name] == 'redirect':
            casalog.showconsole(True)

        # Install filter to remove MSSelectionNullSelection errors
        casalog.filter('NORMAL1')
        casalog.filterMsg('MSSelectionNullSelection')
        casalog.filterMsg('non-existent spw')

        # Post MPI welcome msg
        casalog.post(MPIEnvironment.mpi_info_msg,"INFO",casalog_call_origin)

        # Initialize MPICommandServer and start serving
        server = MPICS.MPICommandServer()
        server.serve()

    else:

        MPIEnvironment.finalize_mpi_environment()
