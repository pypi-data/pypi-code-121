# mu32.core.py python program interface for MegaMicro Mu32 remote receiver 
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
See documentation on usb websocket python programming on https://websockets.readthedocs.io/en/stable/index.html

Please, note that the following packages should be installed before using this program:
	> pip install websockets
"""

import time
import threading
import json
import asyncio
import websockets
import numpy as np

from . import core_base as base
from .log import mulog as log
from .exception import MuException


"""
Default conecting properties
"""
DEFAULT_REMOTE_ADDRESS = 			'127.0.0.1'					# remote receiver network address
DEFAULT_REMOTE_PORT = 				8002						# remote receiver network port


class MegaMicroWS( base.MegaMicro ):
	"""
	MegaMicroWS is a generic websocket interface to MegaMicro receiver designed for handling Mu32 to Mu1024 remote systems
	"""

	
	def __init__( self, remote_ip=DEFAULT_REMOTE_ADDRESS, remote_port=DEFAULT_REMOTE_PORT ):
		"""
		class base receiver properties are note used since system is remote -> set to 0x00
		"""
		super().__init__(
			usb_vendor_id=0x00, 
			usb_vendor_product=0x00,
			usb_bus_address=0x00,
			pluggable_beams_number=0x00
		)

		"""
		Set default values			
		"""
		self._server_address = remote_ip
		self._server_port = remote_port

	def __del__( self ):
		log.info( '-'*20 )
		log.info('MegaMicroWS: end')


	def run( self, **kwargs):
		self.run_setargs( kwargs )

		try:
			"""
			Do some controls and print recording parameters
			"""
			if self._analogs_number > 0:
				log.warning( f"Mu32ws: {self._analogs_number} analogs channels were activated while they are not supported on Mu32 device -> unselecting")
				self._analogs = []
				self._analogs_number = 0
				self._channels_number = self._mems_number + self._analogs_number + self._counter + self._status
				self._buffer_words_length = self._channels_number*self._buffer_length

			log.info( 'Mu32ws: Start running recording...')
			log.info( '-'*20 )
			log.info( ' .sampling frequency: %d Hz' % self._sampling_frequency )

			if self._block == True:
				log.warning( 'Mu32ws: blocking mode is not available in remote mode (set to False)' )
				self._block = False

			self._transfer_thread = threading.Thread( target= self.transfer_loop_thread )
			self._transfer_thread.start()

		except MuException as e:
			log.critical( str( e ) )
			raise
		except Exception as e:
			log.critical( f"Unexpected error:{e}" )
			raise


	def wait( self ):
		if self._block:
			log.warning( "Mu32ws: mu32ws.wait() should not be used in blocking mode" )
			return

		self._transfer_thread.join()

		if self._transfer_thread_exception:
			raise self._transfer_thread_exception

	def is_alive( self ):
		if self._block:
			log.warning( "Mu32ws: mu32ws.is_alive() should not be used in blocking mode" )
			return
		
		return self._transfer_thread.is_alive()

	def stop( self ):
		"""
		Stop the transfer loop
		"""
		self._recording = False

	def transfer_loop_thread( self ):
		asyncio.run( self.transfer_loop() )

	async def transfer_loop( self ):

		log.info( f" .remote Mu32 server address:  {self._server_address}:{self._server_port}" )
		log.info( f" .desired recording duration: {self._duration}s" )
		log.info( f" .minimal recording duration: {( self._transfers_count*self._buffer_length ) / self._sampling_frequency}s" )
		log.info( f" .{self._mems_number} activated microphones" )
		log.info( f" .activated microphones: {self._mems}" )
		log.info( f" .{self._analogs_number} activated analogic channels" )
		log.info( f" .activated analogic channels: {self._analogs }" )
		log.info( f" .whether counter is activated: {self._counter}" )
		log.info( f" .whether counter activity is removed: {self._counter_skip}" )
		log.info( f" .whether status is activated: {self._status}" )
		log.info( f" .total channels number is {self._channels_number}" )
		log.info( f" .datatype: {self._datatype}" )
		log.info( f" .number of USB transfer buffers: {self._buffers_number}" )
		log.info( f" .buffer length in samples number: {self._buffer_length} ({self._buffer_length*1000/self._sampling_frequency} ms duration)" )			
		log.info( f" .buffer length in 32 bits words number: {self._buffer_length}x{self._channels_number}={self._buffer_words_length} ({self._buffer_words_length*base.MU_TRANSFER_DATAWORDS_SIZE} bytes)" )
		log.info( f" .minimal transfers count: {self._transfers_count}" )
		log.info( f" .multi-threading execution mode: {not self._block}" )

		if self._h5_recording:
			log.info( f" .H5 recording: ON" )
			self.h5_log_info()
		else:
			log.info( f" .H5 recording: OFF" )

		try:
			async with websockets.connect( 'ws://' + self._server_address + ':' + str( self._server_port ) ) as websocket:
				"""
				Request run command
				"""
				log.info( f" .connect to server and send running command..." )
				message = json.dumps( {
					'request': 'run',
					'parameters': {
						'sampling_frequency': self._sampling_frequency,
						'mems': self._mems,
						'analogs': self._analogs,
						'counter': self._counter,
						'counter_skip': self._counter_skip,
						'status': self._status,
						'duration': self._duration,
						'buffer_length': self._buffer_length,
						'buffers_number': self._buffers_number
					}
				} )
				await websocket.send( message )
				response = json.loads( await websocket.recv() )
				if response['type'] == 'status' and response['response'] == "OK":
					log.info( " .running command accepted by server" )						
				elif response['type'] == 'error':
					raise MuException( f"Running command failed. Server {self._server_address}:{self._server_port} said:  {response['error']}: {response['message']}" )
				else:
					log.error( f"unexpected server type response `{response['type']}`" )
					raise MuException( f"unexpected server type response `{response['type']}`" )

				"""
				Open H5 file if recording on 
				"""
				if self._h5_recording:
					self.h5_init()

				"""
				Proccess received data and send aknowledgment to server
				"""
				self._transfer_index = 0
				self._recording = True
				while self._recording:
					data = await websocket.recv()
					if isinstance( data, str ):
						input_data = json.loads( data )
						if input_data['type'] == 'error':
							raise MuException( f"Received error message from server: {input_data['type']}: {input_data['response']}" )
						elif input_data['type'] == 'status' and input_data['response'] == 'END':
							log.info( f" .Received end of service from server. Stop running." )
							break
						else:
							raise MuException( f"Received unexpected type message from server: {input_data['type']}" )

					input_data = np.frombuffer( data, dtype=np.int32 )

					"""
					Get current timestamp as it was at transfer start
					"""
					transfer_timestamp = time.time() - self._buffer_duration

					input_data = np.reshape( input_data, ( self._buffer_length, self._channels_number - self._counter_skip ) ).T

					"""
					Remove counter signal is requested
					! NOT OK -> aborting:  index 1 is out of bounds for axis 0 with size 1
					"""
					#if self._counter and self._counter_skip:
					#	input_data = input_data[1:,:]

					"""
					Proceed to buffer recording in h5 file if requested
					"""
					if self._h5_recording:
						try:
							self.h5_write_mems( input_data, transfer_timestamp )
						except Exception as e:
							log.error( f"Mu32: H5 writing process failed: {e}. Aborting..." )
							self._recording = False

					"""
					Call user callback processing function if any.
					Otherwise push data in the object signal queue
					"""
					if self._callback_fn != None:
						try:
							self._callback_fn( self, input_data )
						except KeyboardInterrupt as e:
							log.info( ' .keyboard interrupt during user processing function call' )
							self._recording = False
						except Exception as e:
							log.error( f"Unexpected error {e}. Aborting..." )
							raise
					else:
						self._signal_q.put( input_data )

					"""
					Control duration and stop acquisition if the transfer count is reach
					_transfers_count set to 0 means the acquisition is infinite loop
					"""
					self._transfer_index += 1
					"""
					The problem is to decide which of the client or the server is responsible for counting.
					Until now we are on the server strategy for finite loop. 
					"""
					#if self._transfers_count != 0 and  self._transfer_index > self._transfers_count:
					#	self._recording = False


				if not self._recording:
					"""
					Recording flag False means the stop command comes from the client -> send stop command to the server
					"""
					log.info( ' .send stop command to server...' )
					await websocket.send( json.dumps({ 'request': 'stop'}) )

				if self._h5_recording:
					"""
					Stop H5 recording
					"""
					self.h5_close()

				log.info( ' .end of acquisition' )

		except Exception as e:
			log.error( f"Stop running due to exception: {e}." )
			self._transfer_thread_exception = e
			if self._h5_recording:
				"""
				Stop H5 recording
				"""
				self.h5_close()

