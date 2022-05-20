# Copyright (C) Prizmi, LLC - All Rights Reserved
# Unauthorized copying or use of this file is strictly prohibited and subject to prosecution under applicable laws
# Proprietary and confidential

import os
import warnings
import logging

from learner.engines.engine_manager import EngineHandler
from learner.configuration.configuration import Configuration
from learner.communication.communication_manager import CommunicationHandler
from learner.data_worker.data_mover import DataMoverManager
os.environ["JOBLIB_START_METHOD"] = "forkserver"
warnings.filterwarnings(action='ignore', category=DeprecationWarning)


def main():
    conf = None
    try:
        conf = Configuration()
        # we handle s3 right after we create the conf object
        data_mover = DataMoverManager(conf)
        data_mover.move_data(mode="download")
        EngineHandler(conf)
        data_mover.move_data(mode="upload")
        message = "{timetag}. SUCCESS. CONFIG: {config_filename}".format(timetag=conf.timetag,
                                                                         config_filename=conf.config_filename)
        comm = CommunicationHandler(conf, message=message)
        comm.handle_admin_communication()
    except Exception as e:
        # we still want to upload to s3 (if requested) even if we get an error
        data_mover = DataMoverManager(conf)
        data_mover.move_data(mode="upload")
        try:
            message = "{timetag}. ERROR: '{error}'. CONFIG: {config_filename}.".format(timetag=conf.timetag,
                                                                                       config_filename=conf.config_filename,
                                                                                       error=str(e))
            logging.critical(f"Something went wrong during execution. Here's what we know about the error: {e}")
            comm = CommunicationHandler(conf, message=message)
            comm.handle_admin_communication()
        except AttributeError:
            # if we get here, that means we don't have a conf object. We need to get the info we need and then
            # communicate them.
            logging.critical("Problem in parsing the configuration file. The error is: {error}".format(error=str(e)))
