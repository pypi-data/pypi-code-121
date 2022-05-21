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
Mu32 documentation is available on https://distalsense.io
See documentation on websockets https://websockets.readthedocs.io
For full real time server example see:  https://jackylishi.medium.com/build-a-realtime-dash-app-with-websockets-5d25fa627c7a
Also see: https://www.programcreek.com/python/example/94580/websockets.serve

Please, note that the following packages should be installed before using this program:
    > pip install websockets
"""

"""
To do: 
- catching exception (Keyboard Interupt)
- make the server possible to stop (shutdown)
"""


import asyncio
from ctypes import sizeof
from time import sleep, time_ns
from datetime import datetime
import websockets
import json
import queue
import argparse
import numpy as np

from mu32.log import logging, mulog as log
from mu32.exception import MuException
from mu32.core import Mu32, Mu32usb2, Mu256, Mu1024
from mu32 import beamformer 
from mu32.core_h5 import MuH5

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8002
DEFAULT_MEGAMICRO_SYSTEM = 'Mu32'
DEFAULT_MAX_CONNECTIONS = 5

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
    """
    def __init__( self, maxconnect=DEFAULT_MAX_CONNECTIONS, filename=None ):
        self._host = DEFAULT_HOST
        self._port = DEFAULT_PORT
        self._system = DEFAULT_MEGAMICRO_SYSTEM
        self._connected = {}
        self._maxconnect = maxconnect
        self._cnx_counter = 0
        self._mm = None
        self._parameters = {}
        self._status = {
            'start_time': time_ns(),
            'error': False,
            'last_error_message': '',
            'last_control_time': 0,
            'parameters': {}
        }
        self._is_running = False
        self._h5_filename = filename

        self._svc_counter = 0

        log.info( f"Starting MegaMicro server at {datetime.fromtimestamp(self._status['start_time']//10**9)}" )


    def __del__( self ):
        self._mm = None


    def system_control( self, verbose=True ):
        """
        perform controls before running server
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

        Parameters
        ----------
        megamicro_system: receiver type (Mu32, Mu32usb2, Mu256, Mu1024) 
        host: server host IP
        port: server listening port 
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
            log.error( f"Error while starting server: {e}" )
            self._status['error'] = True
            self._status['last_error_message'] = f"{e}"
        except Exception as e:
            log.critical( f"Failed to start server: {e}" )
            exit()
        else :
            log.info( f" .Connection to receiver and running tests: Ok" )
            log.info( f" .MegaMicro system found: '{self._system}'" )

        """
        All seems ok -> start server and run for ever, waiting for incomming connections
        """
        async with websockets.serve( self.handler, self._host, self._port ):
            log.info( f" .Listening at port {self._host}:{self._port}" )
            result = await asyncio.Future()


    async def handler( self, websocket ):
        """
        Handler launched at every incomming remote client request
        Infinite interaction loop with connected user

        Parameters
        ----------
        websocket: the websocket object opened for client connection handling  
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
                if message['request'] == 'bfdoa':
                    await self.service_bfdoa( websocket, cnx_id, message )
                elif message['request'] == 'status':
                    await self.service_status( websocket, cnx_id, message )
                elif message['request'] == 'parameters':
                    await self.service_parameters( websocket, cnx_id, message )
                elif message['request'] == 'exit':
                    log.info( f" .Received exit request from {websocket.remote_address[0]}:{websocket.remote_address[1]}" )
                    break
                else:
                    """
                    Unknown command -> error response
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
            log.error( f"Unknown exception: {e}" )

        log.info( f" .Connection closed for {websocket.remote_address[0]}:{websocket.remote_address[1]} remote host" )
        del self._connected[str(cnx_id)]
        log.info( f" .Listening at port {self._host}:{self._port}" )


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
        if self._is_running:
            """
            Receiver is running -> cannot perform doa
            """
            await websocket.send( json.dumps( {
                'type': 'error',
                'response': 'NOT OK',
                'error': 'Unable to serve doa request',
                'message': 'Megamicro receiver busy, cannot perform doa',
                'request': message['request']
            }) )
            log.info( f" .Could not serve doa request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: receiver busy" )

        else:
            """
            Perform controls and compute some parameters.
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
        if self._is_running:
            """
            Receiver is running -> cannot perform run
            """
            await websocket.send( json.dumps( {
                'type': 'error',
                'response': 'NOT OK',
                'error': 'Unable to serve run request',
                'message': 'Megamicro receiver busy, cannot perform run'
            }) )
            log.info( f" .Could not serve run request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: receiver busy" )

        else:
            """
            Service accepted -> perform run service
            """
            await websocket.send( json.dumps( {
                'type': 'status',
                'response': 'OK',
                'error': '',
                'message': 'Run service request accepted',
                'status': message['parameters']
            }) )

            """
            Handle MegaMicro run
            We cannot use thread for the sending service becaus it would imply the same websocket in two diffrent threads
            instead, use asyncio.create_task(read_from_websocket(websocket))
            """
            log.info( f" .Start running MegaMicro..." )
            log.info( f" .Run command is: {message['parameters']}" )

            parameters = message['parameters']
            try:
                if self._system == 'Mu32':
                    mm = Mu32()
                elif self._system == 'Mu32usb2':
                    mm = Mu32usb2()
                elif self._system == 'Mu256':
                    mm = Mu256()
                elif self._system == 'Mu1024':
                    mm = Mu1024()
                elif self._system == 'MuH5':
                    if 'h5_play_filename' in message:
                        mm = MuH5( message['h5_play_filename'] )
                    else:
                        mm = MuH5()

                mm.run( parameters = parameters )

                self._mm = mm
                self._status = mm.status
                self._parameters = mm.parameters

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
                data = mm.signal_q.get( block=True, timeout=2 )
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
                    Get a message
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
        if self._is_running:
            """
            Receiver is running -> cannot perform test
            """
            await websocket.send( json.dumps( {
                'type': 'error',
                'response': 'NOT OK',
                'error': 'Unable to serve request',
                'message': 'Megamicro receiver busy, cannot perform running tests'
            }) )
            log.info( f" .Could not serve test request for {websocket.remote_address[0]}:{websocket.remote_address[1]}: receiver busy" )
        else:
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
    Default simple server
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
