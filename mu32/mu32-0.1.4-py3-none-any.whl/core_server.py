# core_server.py python server program for MegaMicro systems 
#
# Copyright (c) 2022 Distalsense
# Author: bruno.gas@distalsense.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
The mu32.core_server module defines a server for using MegaMico receiver through the network.

* Mu32 documentation is available on https://distalsense.io
* See documentation on websockets https://websockets.readthedocs.io
* For full real time server example see:  https://jackylishi.medium.com/build-a-realtime-dash-app-with-websockets-5d25fa627c7a
* Also see: https://www.programcreek.com/python/example/94580/websockets.serve

Please, note that the following packages should be installed before using this program:

.. code-block:: bash

    $ > pip install websockets

To do: 
======
* catching exception (Keyboard Interupt)
* make the server possible to stop (shutdown)
"""


import asyncio
import fnmatch
from os import path, listdir, getcwd
from ctypes import sizeof
from time import sleep, time_ns
from datetime import datetime
from threading import Timer, BoundedSemaphore
import websockets
import json
import queue
import argparse
import numpy as np

from mu32.log import logging, DEBUG_MODE, mulog as log
from mu32.exception import MuException
from mu32.core import Mu32, Mu32usb2, Mu256, Mu1024
from mu32 import beamformer 
from mu32.core_h5 import MuH5

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8002
DEFAULT_MEGAMICRO_SYSTEM = 'Mu32'
DEFAULT_MAX_CONNECTIONS = 5
SRV_MEGAMICRO_MAX_RUN = 1
SRV_SCHEDULER_LIST_MAXSIZE = 100

welcome_msg = '-'*20 + '\n' + 'MegaMicro server program\n \
Copyright (C) 2022  distalsense\n \
This program comes with ABSOLUTELY NO WARRANTY; for details see the source code\'.\n \
This is free software, and you are welcome to redistribute it\n \
under certain conditions; see the source code for details.\n' + '-'*20

#log.setLevel( logging.INFO )

class MegaMicroServer():
    """
    Server for sharing a megamicro receiver among multiple remote users.
    Users can get status and informations from the receiver while it is running but only one user can run the receiver at the same time.
    In case the server is busy, a processing request would wait for current process termination.
    """

    _sched_tasks = []
    _sched_next_id = 0
    _host = DEFAULT_HOST
    _port = DEFAULT_PORT
    _system = DEFAULT_MEGAMICRO_SYSTEM
    _connected = {}
    _maxconnect = DEFAULT_MAX_CONNECTIONS
    _cnx_counter = 0
    _mm = None
    _parameters = {}
    _status = {}
    _svc_counter = 0
    _h5_filename = None
    _megamicro_sem = None
    _h5_rootdir = './'


    def __init__( self, maxconnect=DEFAULT_MAX_CONNECTIONS, filename=None ):

        self._maxconnect = maxconnect
        self._megamicro_sem = BoundedSemaphore( value=SRV_MEGAMICRO_MAX_RUN )
        self._h5_filename = filename
        self._status = {
            'start_time': time_ns(),
            'error': False,
            'last_error_message': '',
            'last_control_time': 0,
            'parameters': {}
        }
        
        """
        Set H5 root directory to current working directory
        """
        self._h5_rootdir = getcwd()

        log.info( f"Starting MegaMicro server at {datetime.fromtimestamp(self._status['start_time']//10**9)}" )


    def __del__( self ):
        self._mm = None
        log.info( f"MegaMicro down at {datetime.fromtimestamp(self._status['start_time']//10**9)}" )


    def system_control( self, verbose=True ):
        """
        Perform controls before running server
        :param verbose: Optionnal 
        :type verbose: bool
        :raise MuException: if the declared system is invalid (Mu32, Mu32usb2, Mu256, Mu1024, MuH5)
        """
        self.error_reset()

        if self._system != 'Mu32' and self._system != 'Mu32usb2' and self._system != 'Mu256' and self._system != 'Mu1024' and self._system != 'MuH5':
            raise MuException( f"Unknown system: `{self._system}`" )

        if self._system == 'Mu32':
            mm = Mu32()
        elif self._system == 'Mu32usb2':
            mm = Mu32usb2()
        elif self._system == 'Mu256':
            mm = Mu256()
        elif self._system == 'Mu1024':
            mm = Mu1024()
        elif self._system == 'MuH5':
            mm = MuH5()

        """
        No control for MuH5 if filename is not specified 
        """
        if self._system == 'MuH5' and self._h5_filename is None:
            log.info( 'No H5 file or directory specified: abort system check' )
            #return
        
        if self._system == 'MuH5':
            log.info( f"Found H5 files: {mm.h5_files}" )

        """
        perform usb connection test and autotest
        """
        mm.check_usb( verbose=verbose )
        mm.run()
        mm.wait()
        self._parameters = mm.parameters
        self._status['last_control_time'] = time_ns()

        """
        All seems correct
        """
        pass


    def error_reset( self ):
        """
        Cleanup the message error buffer
        """
        self._status['error'] = False
        self._status['last_error_message'] = ''


    async def run( self, megamicro_system=DEFAULT_MEGAMICRO_SYSTEM, host=DEFAULT_HOST, port=DEFAULT_PORT ):
        """
        Make controls and start server

        :param megamicro_system: the receiver system type (Mu32, Mu256,...)
        :type megamicro_system: str
        :param host: Optionnal server host IP
        :type host: str
        :param port: Optionnal server listening port
        :type port: int

        """
        self._host = host
        self._port = port
        self._system = megamicro_system

        """
        Perform connection and running tests
        """
        log.info( f" .Start running tests..." )
        try:
            self.system_control()
        except MuException as e:
            log.error( f"Error while starting server: {e}", exc_info=DEBUG_MODE )
            self._status['error'] = True
            self._status['last_error_message'] = f"{e}"
        except Exception as e:
            log.critical( f"Failed to start server: {e}", exc_info=DEBUG_MODE )
            exit()
        else :
            log.info( f" .Connection to receiver and running tests: Ok" )
            log.info( f" .MegaMicro system found: '{self._system}'" )

        """
        All seems ok -> start server and run for ever, waiting for incomming connections
        """
        async with websockets.serve( self.handler, self._host, self._port ):
            log.info( f" .Listening at port {self._host}:{self._port}" )
            try:
                result = await asyncio.Future()
            except KeyboardInterrupt:
                log.error( f" Keyboard interruption" )
            except:
                log.error( f" System interruption", exc_info=DEBUG_MODE )



    async def handler( self, websocket ):
        """
        Handler launched at every incomming remote client request
        Infinite interaction loop with connected user

        :param websocket: the websocket object opened for client connection handling
        """

        if len( self._connected ) > self._maxconnect:
            """
            Simultaneous connections number is limited to 'maxconnect'
            """
            log.info( f" .Could not accept connexion from {websocket.remote_address[0]}:{websocket.remote_address[1]}: too many connections" )
            await websocket.send( json.dumps( {
                'type': 'error',
                'response': 'NOT OK',
                'error': 'Connexion refused', 
                'message': 'Too many connections' 
            }) )
            log.info( f" .Listening at port {self._host}:{self._port}" )
            return

        """
        Connection accepted -> create a client entry and launch the service handler
        """
        log.info( f" .Accepting connexion from {websocket.remote_address[0]}:{websocket.remote_address[1]}" )
        self._cnx_counter +=1
        cnx_id = self._cnx_counter
        self._connected[str(cnx_id)] = {
            'websocket': websocket , 
            'host': websocket.remote_address[0], 
            'port': websocket.remote_address[1]
        }

        try:
            """
            Check if request can be addressed by the server.
            If not -> return 
            """
            while True:
                message = await websocket.recv()
                message = json.loads( message )
                if message['request'] == 'run':
                    await self.service_run( websocket, cnx_id, message )
                elif message['request'] == 'bfdoa':
                    await self.service_bfdoa( websocket, cnx_id, message )
                elif message['request'] == 'status':
                    await self.service_status( websocket, cnx_id, message )
                elif message['request'] == 'parameters':
                    await self.service_parameters( websocket, cnx_id, message )
                elif message['request'] == 'scheduler':
                    await self.service_scheduler( websocket, cnx_id, message )
                    await websocket.close( reason='Service is done' )
                elif message['request'] == 'h5handler':
                    await self.service_h5handler( websocket, cnx_id, message )     
                    await websocket.close( reason='Service is done' )
                elif message['request'] == 'exit':
                    log.info( f" .Received exit request from {websocket.remote_address[0]}:{websocket.remote_address[1]}" )
                    break
                else:
                    """
                    Unknown request -> error response
                    """
                    await websocket.send( json.dumps( {
                        'type': 'error',
                        'response': 'NOT OK',
                        'error': 'Unable to serve request',
                        'message': 'Unknown or invalid request'
                    }) )
                    log.info( f" .Could not serve request from {websocket.remote_address[0]}:{websocket.remote_address[1]}: unknown or invalid request {message['request']}" )

        except websockets.ConnectionClosedOK:
            log.info( f" .Connexion closed by peer" )
        except websockets.ConnectionClosedError as e:
            if e.rcvd.code == 1005:
                log.info( f" .Connection closed by peer without code status" )
            else:
                log.info( f" .Connection closed by peer with status error: [{e.rcvd.code}]: {e.rcvd.reason}" )
        except websockets.ConnectionClosed:
            log.error( f"Try interacting with remote host on a closed connection" )
        except websockets.WebSocketException as e:
            log.error( f"Unknown websocket exception: {e}" )
        except MuException as e:
            log.info( f" .{e}" )
        except Exception as e:
            log.error( f"Unknown exception: {e}", exc_info=DEBUG_MODE )
        except KeyboardInterrupt:
            log.error( f"Keyboard interruption" )
        except :
            log.critical( f"System interruption", exc_info=DEBUG_MODE  )

        log.info( f" .Connection closed for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote host" )
        del self._connected[str(cnx_id)]
        log.info( f" .Listening at port {self._host}:{self._port}" )



    async def service_h5handler( self, websocket, cnx_id, message ):
        """
        Execute a H5 file management request according message content. 

        * On error: send an error response message to client, then close connection and leave
        * On success: send an aknowledgment message with response to client, then close connection and leave.

        :param websocket: the websocket object opened for client connection handling
        :param message: client message with task parameters
        :type message: dict

        .. code-block:: python

            message = {
                'request': 'h5handler',         # the client request
                'parameters': {                 # dicttionary of task parameters
                    'command': str              # the command to execute
                    ...                         # command parameters
                }
            }
        """
        log.info( f" .Handle H5 management request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )

        """
        Perform controls.
        Please consider these controls as important since not controled error may raise an exception and close the connection.
        """
        if 'parameters' not in message:
            await self.service_h5handler_error( websocket, 'Bad request with missing parameters' )
            return
        parameters = message['parameters']

        if 'command' not in parameters:
            await self.service_h5handler_error( websocket, 'Bad request with missing command' )
            return

        """
        Execute H5 command 
        """
        command = parameters['command']
        if command == 'h5cd':
            """
            Check path existance then set H5 files root directory
            The path can be absolute or not. If not, then the local path is the directory from which the server has been started  
            """

            if 'path' not in parameters:
                await self.service_h5handler_error( websocket, 'Bad request with missing parameter `path`' )
                return

            if not path.exists( parameters['path'] ): 
                await self.service_h5handler_error( websocket, f"Change dir failed: path {parameters['path']} does not exist" )
                return

            self._h5_rootdir = parameters['path']

            await websocket.send( json.dumps( {
                'type': 'response',
                'response': 'OK'
            }) )
            log.info( f" .Changed root dH5 directory to {parameters['path']} for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )     

        elif command == 'h5ls':
            """
            List curent H5 files root directory
            """

            try:
                files = fnmatch.filter( listdir( self._h5_rootdir ), '*.h5' )
            except Exception as e:
                await self.service_h5handler_error( websocket, f"h5ls command failed: {e}" )
            else:
                await websocket.send( json.dumps( {
                    'type': 'response',
                    'response': files
                }) )
                log.info( f" .List H5 files directory for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )     
        
        elif command == 'h5pwd':
            """
            Get current absolute path
            """

            try:
                rootdir = path.abspath( self._h5_rootdir )
            except Exception as e:
                await self.service_h5handler_error( websocket, f"h5pwd command failed: {e}" )
            await websocket.send( json.dumps( {
                'type': 'response',
                'response': rootdir
            }) )
            log.info( f" .Get H5 root directory for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )   

        elif command == 'h5cwd':
            """
            Get default absolute path (current working directory)
            """

            try:
                cwddir = getcwd()
            except Exception as e:
                await self.service_h5handler_error( websocket, f"h5cwd command failed: {e}" )
            await websocket.send( json.dumps( {
                'type': 'response',
                'response': cwddir
            }) )
            log.info( f" .Get H5 default directory for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )   

        else:
            await self.service_h5handler_error( websocket, f"Request failed: unknown command `{command}`" )
            return


    async def service_h5handler_error( self, websocket, msg: str ):
        """
        Send error message to client
        """
        await websocket.send( json.dumps( {
            'type': 'error',
            'response': 'NOT OK',
            'error': 'Unable to serve H5 handler request',
            'message': msg
        }) )
        log.info( f" .Could not serve H5 management request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: {msg}" )


    def _sched_cleanup( self ):
        """
        Free the scheduler task list by freeing completed tasks
        """
        log.info( f" .Cleanup scheduler task list" )
        for index, task in enumerate( self._sched_tasks ):
            if task['status'] == 'complete':
                self._sched_tasks.pop( index )


    def _sched_set_status( self, task_id: int, status: str, message: str=None ):
        """
        Set the status of a task

        :param task_id: the task identifier in the scheduler list
        :type task_id: int
        :param status: the task status to set ('pending', 'active', 'completed', 'error')
        :type status: str
        :param message: Optionnal set the message field
        :type message: str
        """
        for task in self._sched_tasks:
            if task['task_id'] == task_id:
                task['status'] = status
                if message is not None:
                    task['message'] = message
                break


    def _sched_get_status( self, task_id: int ):
        """
        Get the status of a job

        :param task_id: the task identifier in the scheduler list
        :type task_id: int
        :return: the status or False if not found
        :rtype: str|bool
        """

        for task in self._sched_tasks:
            if task['task_id'] == task_id:
                return task['status']

        return False


    def _sched_check_conflict( self, start, stop ):
        """
        Check whether there is a conflict or not between statrt and stop inputs and resgistered pending or active job in the scheduler stack

        :param start: time starting (timestamp)
        :type start: timestamp
        :param stop: time to stop the job (timestamp)
        :type stop: timestamp
        :return: True or False wheter there is a conflict or not
        :rtype: bool
        """

        for task in self._sched_tasks:
            if task['status'] == 'pending' or task['status'] != 'active':
                if ( ( ( datetime.fromtimestamp( start ) - datetime.fromtimestamp( task['parameters']['sched_start_time'] ) ).total_seconds() > 0
                    and ( datetime.fromtimestamp( task['parameters']['sched_stop_time'] ) - datetime.fromtimestamp( start ) ).total_seconds() > 0 )
                    or ( ( datetime.fromtimestamp( stop ) - datetime.fromtimestamp( task['parameters']['sched_start_time'] ) ).total_seconds() > 0 
                    and ( datetime.fromtimestamp( task['parameters']['sched_stop_time'] ) - datetime.fromtimestamp( stop ) ).total_seconds() > 0 )
                ):
                    """
                    Conflict detected.
                    """
                    return True
        
        return False

    def _sched_job_list( self ):
        """
        List all job in the scheduler stack with their status

        :return: array of dictionnaries describing scheduled jobs and status 
        :rtype: list[dict] 
        """

        jobs = []
        for task in self._sched_tasks:
            start = datetime.fromtimestamp( task['parameters']['sched_start_time'] )
            stop = datetime.fromtimestamp( task['parameters']['sched_stop_time'] )
            duration = (stop - start ).total_seconds()
            jobs.append( {
                'task_id': task['task_id'],
                'command': task['command'],
                'planned start': str( start ),
                'planned stop': str( stop ),
                'duration': duration,
                'parameters': task['parameters'],
                'status': task['status'],
                'message': task['message'],
            } )

        return jobs


    def _sched_job_remove( self, task_id: int ):
        """
        Remove a job from the sheduler job stack
        
        :param task_id: the job identifier in the stack
        :type task_id: int
        :return: True on succes, False otherwise
        :rtype: bool
        """

        to_be_removed_key = False
        for index, task in enumerate( self._sched_tasks ):
            if task['task_id'] == task_id:
                to_be_removed_key = index
                break

        if to_be_removed_key is False:
            return False
        else:
            self._sched_tasks.pop( to_be_removed_key )
            return True


    async def service_scheduler( self, websocket, cnx_id, message ):
        """
        Execute a job scheduling request according message content. 
        Task timing is controled such as to prevent from conflicts with other scheduled tasks.

        * On error: send an error response message to client, then leave
        * On success: send an aknowledgment message to client and schedule the task, then leave.

        :param websocket: the websocket object opened for client connection handling
        :param message: client message with task parameters
        :type message: dict

        .. code-block:: python

            message = {
                'request': 'scheduler',         # the client request
                'parameters': {                 # dicttionary of task parameters
                    'command': str              # the command to schedule
                    'sched_start_time': int     # timestamp indicating the exact starting time
                    'sched_stop_time': int      # timestamp indicating the time to stoip the task
                    ...                         # MegaMicro usual parameters or others
                }
            }
        """
        log.info( f" .Handle scheduling request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )

        """
        Perform controls.
        Please consider these controls as important since not controled error may raise an exception and close the connection.
        """
        if 'parameters' not in message:
            await self.service_scheduler_error( websocket, 'Bad request with missing parameters' )
            return
        parameters = message['parameters']

        if 'command' not in parameters:
            await self.service_scheduler_error( websocket, 'Bad request with missing command' )
            return

        """
        Cleanup the scheduler task list if needed
        """
        if len( self._sched_tasks ) > SRV_SCHEDULER_LIST_MAXSIZE:
            self._sched_cleanup()

        """
        Schedule the task 
        """
        try:
            command = parameters['command']
            if command == 'run':
                parameters['task_id'] = self._sched_next_id

                if 'sched_start_time' not in parameters or 'sched_stop_time' not in parameters:
                    await self.service_scheduler_error( websocket, 'Bad request with missing `sched_start_time` or `sched_stop_time` timestamp parameters' )
                    return

                start =  parameters['sched_start_time']
                stop =  parameters['sched_stop_time']
                if stop <= start:
                    await self.service_scheduler_error( websocket, 'Bad request with incoherent start and stop timestamps' )
                    return

                """
                Look for possible conflicts with pending and active tasks
                """
                if self._sched_check_conflict( start, stop ):
                    await self.service_scheduler_error( websocket, 'Conflicting timing with tasks already scheduled' )
                    return 

                """
                Schedule the task
                """
                task = Timer( 2, self.service_scheduler_handler, kwargs=parameters )
                task.start()
                log.info( f" .task {command} scheduled at time {start}" )
                self._sched_tasks.append( {
                    'task_id': self._sched_next_id,
                    'task': task,
                    'command': command,
                    'parameters':parameters,
                    'status': 'pending',
                    'message': ''
                } ) 
                self._sched_next_id += 1

                """
                Sends aknowledgement to client
                """
                await websocket.send( json.dumps( {
                    'type': 'response',
                    'response': 'OK',
                    'message': 'successfull request'
                }) )
                log.info( f" .Scheduled task for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )

            elif command == 'lsjob':
                """
                List jobs in the scheduler stack
                """   

                jobs = self._sched_job_list()

                await websocket.send( json.dumps( {
                    'type': 'response',
                    'response': jobs
                }) )
                log.info( f" .Sent scheduler job list for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )           


            elif command == 'rmjob':
                """
                Remove a job from the scheduler stack
                """

                if 'task_id' not in parameters:
                    await self.service_scheduler_error( websocket, 'Bad request: task_id identifier is missing' )
                    return
                
                task_id = parameters['task_id']

                if status := self._sched_get_status( task_id ) == False:
                    await self.service_scheduler_error( websocket, f"Failed to remove job {task_id}: job not found" )
                    return
                elif status == 'active':
                    await self.service_scheduler_error( websocket, f"Failed to remove job {task_id}: job is active" )
                    return                 
                elif self._sched_job_remove( task_id ) == False:
                    await self.service_scheduler_error( websocket, f"Failed to remove job {task_id}: unknown error" )
                    return
                else:
                    await websocket.send( json.dumps( {
                        'type': 'response',
                        'response': 'OK'
                    }) )
                    log.info( f" .Removed job id [{task_id}] from scheduler stack for {websocket.remote_address[0]}:{websocket.remote_address[1]}" )

            else:
                await self.service_scheduler_error( websocket, f"Bad request with unknown command `{command}`" )
                return            

        except Exception as e:
            """
            Intercept low level exceptions (stop propagate them)
            Error are managed in the try block below so this bloc protect from low level unknown exceptions
            """
            await self.service_scheduler_error( websocket, f"Job exec failed: {e}" )



    def service_scheduler_handler( self, **kwargs ):
        """
        Handle jobs execution on timer request.
        This is a standalone execution provided the MegaMicro receiver is free 
        """
        command = kwargs.get( 'command' )
        log.info( f" .executing task {command} at ..." )
 
        if command == 'run':
            self.service_scheduler_handler_run( parameters=kwargs )

        

    def service_scheduler_handler_run( self, parameters ):
        """
        Handle run job execution.

        :param parameters: dictionary of MegaMicro parameters for job running
        :type parameters: dict
        """
        task_id = parameters['task_id']

        """
        Update duration parameter since the run command accept duration but not time stopping
        """
        duration = ( datetime.fromtimestamp( parameters['sched_stop_time'] ) - datetime.fromtimestamp( parameters['sched_start_time'] ) ).total_seconds()
        parameters['duration'] = duration

        """
        Force H5 recording otherwise data are lost. 
        Client may have given precise informations about H5 registering (directory, filenames, file features, etc.). We should not change them.
        If not system H5 default values will preval.
        """
        parameters['h5_recording'] = True

        log.info( f" .Task [{task_id}] ready for run at {datetime.now()}" )

        with self._megamicro_sem:
            """
            Wait until megamicro is free and then run 
            """
            self._sched_set_status( task_id, 'active' )
            log.info( f" .Task [{task_id}] starting at {datetime.now()} with {duration}s duration" )

            try:
                mm = Mu32()
                mm.run( 
                    h5_recording = True,
                    duration = duration,
                    parameters = parameters
                )
                mm.wait()

            except Exception as e:
                """
                General exception: error is reported on job status and the job is stopped
                """
                self._sched_set_status( task_id, 'error', message = str( e ) )
                log.info( f" .Task [{task_id}]: failed with error: {e}" )
            else:
                self._sched_set_status( task_id, 'completed' )
                log.info( f" .Task [{task_id}]: completed" )



    async def service_scheduler_error( self, websocket, msg: str ):
        """
        Send an error message to client
        """
        await websocket.send( json.dumps( {
            'type': 'error',
            'response': 'NOT OK',
            'error': 'Unable to serve scheduling request',
            'message': msg
        }) )
        log.info( f" .Could not serve scheduling request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: {msg}" )


    async def service_bfdoa( self, websocket, cnx_id, message ):
        """
        Performs doa with classical beamformer algorithm and send data to remote host
        Following parameter values shouyld be set:
        - sampling_frequency
        - mems
        - inter_mems
        - duration
        - beams_number
        - buffer_length
        - buffer_number
        """
        
        log.info( f" .Handle doa request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )

        with self._megamicro_sem:
            """
            Wait until megamicro is free, then perform controls and compute some parameters.
            Please consider these controls as important since not controled errors raise exception and close the connection.
            """
            error = False
            parameters = message['parameters']
            frame_duration = parameters['buffer_length'] / parameters['sampling_frequency']
            if 'inter_mems' not in parameters:
                error = f"Inexistant or bad value for parameter 'inter_mems'"
            elif 'beams_number' not in parameters:
                error = f"Inexistant or bad value for parameter 'beams_number'"

            if error:
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'NOT OK',
                    'error': 'Unable to serve doa request',
                    'message': error,
                    'request': message['request']
                }) )
                log.info( f" .Could not serve doa request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: {error}" )
                return

            """
            Service accepted -> perform doa service
            """
            await websocket.send( json.dumps( {
                'type': 'status',
                'response': 'OK',
                'error': '',
                'message': 'DOA service request accepted',
                'status': parameters,
                'request': message['request']
            }) )

            log.info( f" .Start running MegaMicro for DOA computing..." )
            log.info( f" .DOA run command is: {parameters}" )
            try:
                log.info( f" .Init DOA beamformer with frame length of {frame_duration} s ({parameters['buffer_length']} samples) at sampling frequency {parameters['sampling_frequency']} Hz" )
                antenna=[[0, 0, 0], parameters['mems_number'] , 0, parameters['inter_mems']]
                G = beamformer.das_former( antenna, parameters['beams_number'], sf=parameters['sampling_frequency'], bfwin_duration=frame_duration )
                if self._system == 'Mu32':
                    mm = Mu32()
                elif self._system == 'Mu32usb2':
                    mm = Mu32usb2()
                elif self._system == 'Mu256':
                    mm = Mu256()
                elif self._system == 'Mu1024':
                    mm = Mu1024()
                elif self._system == 'MuH5':
                    mm = MuH5()

                log.info( f"Run {self._system} with duration {parameters['duration']}" )
                mm.run( 
                    mems=parameters['mems'],					# activated mems	
                    duration = parameters['duration'],
                    buffer_length = parameters['buffer_length'],
                    buffers_number = parameters['buffers_number'],
                    sampling_frequency = parameters['sampling_frequency'],
                    h5_recording = parameters['h5_recording'],
                    h5_start_time = parameters['h5_start_time']
                )

                self._mm = mm
                self._status = mm.status
                self._parameters = mm.parameters

                log.info( f"Start handler service bfdoa Mu32 with message {message}" )
                transfer_send_recv = asyncio.create_task ( self.handler_service_bfdoa( websocket, cnx_id, message, G ) )
                await transfer_send_recv

                mm.wait()

            except MuException as e:
                mm.wait()
                log.warning( f"MegaMicro running stopped: {e}" ) 
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'NOT OK',
                    'error': 'Unable to serve request',
                    'message': f"Megamicro running stopped: {e}",
                    'request': message['request']
                }) )
                log.warning( f" .Megamicro running for {websocket.remote_address[0]}:{websocket.remote_address[1]} stopped: {e}" )


    async def handler_service_bfdoa( self, websocket, cnx_id, message, G ):
        """
        data send/receipt loop with client fot DOA results sending
        stop on empty queue or on cancel exception or on stop received message
        """
        log.info( " .Handler service running..." )
        mm = self._mm
        frame_duration = mm.buffer_length / mm.sampling_frequency

        while True:
            """
            get queued signals and send them
            """
            try:
                data = mm.signal_q.get( block=True, timeout=2 )
                powers, beams_number = beamformer.das_doa( 
                    G,
                    data * mm.sensibility,
                    sf = mm.sampling_frequency, 
                    bfwin_duration = frame_duration
                )
                """
                ! Warning: verify whether powers should be transposed or not before sending to the net...
                """
                output = powers.tobytes()
                await websocket.send( output )
                try:
                    recv_text=await asyncio.wait_for( websocket.recv(), timeout=0.0001 )
                except asyncio.TimeoutError:
                    pass
                else:
                    recv_text = json.loads( recv_text )
                    if recv_text['request'] == 'stop':
                        log.info( " .Received stop message..." )
                        self._mm.stop()

            except queue.Empty:
                break

            except asyncio.CancelledError:
                log.info( f" .Stop service due to cancellation request" )
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'END',
                    'error': 'Service cancelled',
                    'message': 'Service cancelled for unknown reason',
                    'request': message['request']
                }) )
                self._mm.stop()
                return
                
            except Exception as e:
                log.info( f" .Stop service for remote host {websocket.remote_address[0]}:{websocket.remote_address[1]} due to exception throw: {e}" )
                self._mm.stop()
                raise e

        """
        Regular end of service
        """
        await websocket.send( json.dumps( {
            'type': 'status',
            'response': 'END',
            'error': '',
            'message': 'End of service',
            'status': self._mm.status,
            'request': message['request']
        }) )
        log.info( f" .End of DOA service for client {websocket.remote_address[0]}:{websocket.remote_address[1]}" )


    async def service_run( self, websocket, cnx_id, message ):
        """
        Performs run and send samples to the remote host
        """
        log.info( f" .Handle run request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )
        await websocket.send( json.dumps( {
            'type': 'status',
            'response': 'OK',
            'error': '',
            'message': 'Run service request accepted',
            'status': message['parameters']
        }) )

        with self._megamicro_sem:
            """
            Handle MegaMicro run. Wait until megamicro is free, then perform run service
            We cannot use thread for the sending service because it would imply the same websocket in two different threads.
            Instead, use asyncio.create_task(read_from_websocket(websocket))
            """
            log.info( f" .Start running MegaMicro..." )
            log.info( f" .Run command is: {message['parameters']}" )

            parameters = message['parameters']
            try:
                """
                Declare the MegaMicro system that will get data.
                Note that the server can serve H5 files even if a receiver Mu32-1024 is connected.
                We have to look for a client request for a H5 playing before using the default connected system.
                """
                if ( 'system' in parameters and parameters['system'] == 'MuH5' ) or self._system == 'MuH5':
                    log.info( f"Set the MegaMicro MuH5 system" )
                    if 'h5_play_filename' in parameters:
                        mm = MuH5( parameters['h5_play_filename'] )
                    else:
                        mm = MuH5()
                elif self._system == 'Mu32':
                    mm = Mu32()
                elif self._system == 'Mu32usb2':
                    mm = Mu32usb2()
                elif self._system == 'Mu256':
                    mm = Mu256()
                elif self._system == 'Mu1024':
                    mm = Mu1024()

                """
                Start asynchronous run (dedicaced thread) 
                """
                mm.run( parameters = parameters )

                self._mm = mm
                self._status = mm.status
                self._parameters = mm.parameters

                """
                Start asynchronous data sending task through the network (coroutine)
                """
                transfer_send_recv = asyncio.create_task ( self.handler_service_run( websocket, cnx_id, message ) )
                await transfer_send_recv

                mm.wait()

            except MuException as e:
                mm.wait()
                log.warning( f"MegaMicro running stopped: {e}" ) 
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'NOT OK',
                    'error': 'Unable to serve request',
                    'message': f"Megamicro running stopped: {e}"
                }) )
                log.warning( f" .Megamicro running for {websocket.remote_address[0]}:{websocket.remote_address[1]} stopped: {e}" )


    async def handler_service_run( self, websocket, cnx_id, message ):
        """
        data send/receipt loop with client
        stop on empty queue or on cancel exception or on stop received message
        """
        log.info( " .Handler service running..." )
        mm = self._mm
        while True:
            """
            get queued signals and send them
            """
            try:
                """
                Get from queue and send
                """
                data = mm.signal_q.get( block=True, timeout=2 ).T
                output = data.tobytes()
                await websocket.send( output )
                
                try:
                    """
                    Check for incomming message from client
                    """
                    recv_text=await asyncio.wait_for( websocket.recv(), timeout=0.0001 )
                except asyncio.TimeoutError:
                    """
                    No pending message -> continue
                    """
                    pass
                else:
                    """
                    Get a message (only stop messages are considered until now. Will be extended in the futur)
                    """
                    recv_text = json.loads( recv_text )
                    if recv_text['request'] == 'stop':
                        log.info( " .Received stop message..." )
                        self._mm.stop()

            except queue.Empty:
                break

            except asyncio.CancelledError:
                log.info( f" .Stop service due to cancellation request" )
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'END',
                    'error': 'Service cancelled',
                    'message': 'Service cancelled for unknown reason'
                }) )
                self._mm.stop()
                return
                
            except Exception as e:
                log.info( f" .Stop service for remote host {websocket.remote_address[0]}:{websocket.remote_address[1]} due to exception throw: {e}" )
                """
                The connection may be broken so we should not send message but just closing the service...
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'END',
                    'error': 'Exception',
                    'message': f"{e}"
                }) )
                """
                self._mm.stop()
                raise e

        """
        Regular end of service
        """
        await websocket.send( json.dumps( {
            'type': 'status',
            'response': 'END',
            'error': '',
            'message': 'End of service',
            'status': self._mm.status
        }) )
        log.info( f" .End of run service for client {websocket.remote_address[0]}:{websocket.remote_address[1]}" )



    async def service_status( self, websocket, cnx_id, message ):
        """
        return current status to remote host
        """
        log.info( f" .Handle status request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )
        await websocket.send( json.dumps( {
            'type': 'status',
            'response': 'OK',
            'error': '',
            'message': 'Status request accepted',
            'status': self._status
        }) )


    async def service_parameters( self, websocket, cnx_id, message ):
        """
        Performs autotest and send current MegaMicro parameters
        """
        log.info( f" .Handle parameters request for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote client" )
        with self._megamicro_sem:
            try:
                self.system_control( verbose=False )
            except MuException as e:
                """
                Send error response
                """
                await websocket.send( json.dumps( {
                    'type': 'error',
                    'response': 'NOT OK',
                    'error': 'Autotest failed',
                    'message': f"{e}"
                }) )
                log.warning( f" .Autotest running failed. Could not serve request from {websocket.remote_address[0]}:{websocket.remote_address[1]}" )        
            else:
                """
                Send response
                """
                await websocket.send( json.dumps( {
                    'type': 'parameters',
                    'response': 'OK',
                    'error': '',
                    'message': 'Parameters request accepted',
                    'parameters': self._parameters
                }) )



async def main():
    """
    Default simple server. This is a use case example. Please use the mu32-server program instead.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument( "-n", "--host", help=f"set the server listening host. Default is {DEFAULT_HOST}" )
    parser.add_argument( "-p", "--port", help=f"set the server listening port. Default is {DEFAULT_PORT}" )
    parser.add_argument( "-s", "--system", help=f"set the MegaMicro receiver type system (Mu32, Mu256, Mu1024, MuH5). Default is {DEFAULT_MEGAMICRO_SYSTEM}" )
    parser.add_argument( "-c", "--maxconnect", help=f"set the server maximum simultaneous connections. Default is {DEFAULT_MAX_CONNECTIONS}" )
    parser.add_argument( "-f", "--file", help=f"set the server in H5 file reader mode on specified file or directory. Default is None" )
    args = parser.parse_args()
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    megamicro_system = DEFAULT_MEGAMICRO_SYSTEM
    maxconnect = DEFAULT_MAX_CONNECTIONS
    filename = None
    if args.host:
        host = args.host
    if args.port:
        port = args.port
    if args.system:
        megamicro_system = args.system
    if args.maxconnect:
        maxconnect = args.maxconnect
    if args.file:
        filename = args.file

    print( welcome_msg )

    try:
        server = MegaMicroServer( maxconnect=maxconnect, filename=filename )
        result = await server.run(
            megamicro_system=megamicro_system,
            host=host,
            port=port
        )
    except MuException as e:
        log.error( f"Server abort due to internal error: {e}" )
    except Exception as e:
        log.error( f"Server abort due to unknown error: {e}" )



if __name__ == "__main__":
    asyncio.run( main() )
