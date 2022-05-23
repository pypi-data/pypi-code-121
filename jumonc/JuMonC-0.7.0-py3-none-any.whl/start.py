import logging

import mpi4py
from mpi4py import MPI

from threading import Thread

import sys

from typing import Any


from JuMonC import settings
from JuMonC._version import __version__
from JuMonC.helpers.startup import communicateAvaiablePlugins
from JuMonC.helpers.cmdArguments import parseCMDOptions
from JuMonC.models.plugins import gatherRESTpaths, startPlugins, registerRESTpaths



logger = logging.getLogger(__name__)
logging.info("Running JuMonC with version: %s", __version__)

mpi4py.rc.threads = True
mpi4py.rc.thread_level = "funneled"

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

def startJuMonC() -> None:
    parseCMDOptions(sys.argv[1:])
    startPlugins()
    communicateAvaiablePlugins()

    #pylint: disable=import-outside-toplevel
    if rank == 0:
        from JuMonC.handlers.base import RESTAPI
        from JuMonC.handlers import main
    
        from JuMonC.tasks import mpiroot
        from JuMonC.models.cache.database import Base, engine, db_session
        
        gatherRESTpaths()
    
        main.registerRestApiPaths()
        registerRESTpaths()

        if settings.SSL_ENABLED:
            JuMonC_SSL = settings.SSL_MODE
        else:
            JuMonC_SSL = None

        flask_thread = Thread(target=RESTAPI.run, kwargs={'debug': True, 'port': settings.REST_API_PORT, 'use_reloader': False, 'ssl_context': JuMonC_SSL})
        flask_thread.start()
        
        from JuMonC.models.cache import dbmodel
        Base.metadata.create_all(bind=engine)
        dbmodel.check_db_version()

        @RESTAPI.teardown_appcontext
        def shutdown_session(exception:Any = None) -> None:
            db_session.remove()
            if exception:
                logging.warning("DB connection close caused exception: %s", str(exception))
        
    
    
        mpiroot.waitForCommands()
    
    
        flask_thread.join()
    
    else:
        from JuMonC.tasks import mpihandler
    
        mpihandler.waitForCommands()
    #pylint: enable=import-outside-toplevel
        
