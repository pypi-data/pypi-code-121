# mu32.core_h5.py python program interface for MegaMicro Mu32 receiver 
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
See documentation on usb device programming with libusb on https://pypi.org/project/libusb1/1.3.0/#documentation
Examples are available on https://github.com/vpelletier/python-libusb1

Please, note that the following packages should be installed before using this program:
	> pip install h5py
"""

from operator import index
import os
import sys
import h5py
import threading
import json
import numpy as np
import queue
from time import sleep

from mu32.log import logging, mulog as log, mu32log		# mu32log for backward compatibility
from mu32.exception import Mu32Exception, MuException
from mu32.core_base import MegaMicro, MU_TRANSFER_DATAWORDS_SIZE, MU_BEAM_MEMS_NUMBER


DEFAULT_H5_PLAY_FILENAME			= './'


log.setLevel( logging.INFO )

class MuH5( MegaMicro ):
	"""
	MuH5 is the base class for getting array signals stored in H5 files 
	"""
	_h5_files= list()
	_h5_current_file = None
	_h5_current_filename = ''
	_h5_parameters = None
	_h5_playing = False
	_h5_dataset_index = 0
	_h5_dataset_index_ptr = 0
	_h5_start_time = 0
	_h5_run_kwargs = None
	_h5_ctrl_thread = None
	_h5_ctrl_thread_exception: MuException = None

	@property
	def h5_files( self ):
		return self._h5_files

	def __init__( self, filename=DEFAULT_H5_PLAY_FILENAME ):
		"""
		Get H5 file or directory.
		"""
		self._h5_files= list()
		if os.path.isdir( filename ):
			for file in os.listdir( filename ):
				if file.endswith( '.h5' ):
					self._h5_files.append( file )
		elif os.path.exists( filename ):
			self._h5_files.append( filename )
		else:
			log.error( f"Unable to create object MuH5: file `{filename}` doesn't exist" )
			raise MuException( f"Unable to create object MuH5: file `{filename}` doesn't exist" )


	def __del__( self ):
		log.info( '-'*20 )
		log.info('MuH5: end')

	def check_usb( self, verbose=True ):
		pass

	def processRun():
		pass

	def run_setargs( self, kwargs ):
		"""
		Set base arguments. if no argument given, the run_setargs() set the MegaMicro.autotest() method as post callback
		"""
		super().run_setargs( kwargs )

		"""
		Set specific arguments for playing H5 files
		"""
		h5_play_filename = None
		if kwargs.get('h5_play_filename') is not None:
			h5_play_filename=kwargs.get('h5_play_filename')
		if kwargs.get('h5_start_time') is None: h5_start_time = 0
		else: h5_start_time = kwargs.get('h5_start_time')
		if kwargs.get('parameters') is None: parameters = None
		else: parameters = kwargs.get('parameters')

		if parameters is not None:
			h5_play_filename = None
			h5_start_time = 0

			if 'h5_play_filename' in parameters:
				h5_play_filename = parameters['parameters']
			if 'h5_start_time' in parameters:
				h5_start_time = parameters['h5_start_time']			

		if h5_play_filename is not None:
			"""
			A new playing file or directory is given as argument -> change default or initial one:
			"""
			files = list()
			if os.path.isdir( h5_play_filename ):
				for file in os.listdir( h5_play_filename ):
					if file.endswith( '.h5' ):
						files.append( file )
			elif os.path.exists( h5_play_filename ):
				files.append( h5_play_filename )
			else:
				log.error( f"Unable to run: file or directory `{h5_play_filename}` doesn't exist" )
				raise MuException( f"Unable to run: file or directory `{h5_play_filename}` doesn't exist" )			

			if files:
				self._h5_files = files

		self._h5_start_time = h5_start_time



	def run( self, **kwargs ):
		if not self._h5_files:
			log.error( f"No H5 file: unable to run. Aborting run service..." )
			raise MuException( f"No H5 file: unable to run. Aborting run service..." )

		self._h5_run_kwargs = kwargs

		"""
		Start control thread.
		Ctrl_thread() run and control the transfer process thread and manage H5 files
		"""
		log.info( f" .Processing transfer")
		log.info( '-'*20 )

		if self._block:
			"""
			Blocking mode: no thread
			"""
			self.ctrl_thread()
		else: 
			self._h5_ctrl_thread = threading.Thread( target= self.ctrl_thread )
			self._h5_ctrl_thread.start()


	def ctrl_thread( self ):

		for index, h5_file in enumerate( self._h5_files ):
			self._h5_current_filename = h5_file
			if index > 0:
				"""
				Reset starting time for next files
				"""
				self._h5_start_time = 0

			"""
			Loop on all available H5 files
			"""
			try:
				self.transfer_loop()
			except MuException as e:
				log.critical( str( e ) )
				self._h5_ctrl_thread_exception = e
			except Exception as e:
				log.critical( f"Unexpected error:{e}" )
				self._h5_ctrl_thread_exception = e

		log.info( f" .End of control thread" )


	def transfer_loop( self ):
		"""
		! Note that continuity between files is not managed
		! Timing should be improved
		! sub list of MEMs is not handled (eg [0, 1, 2] instead of complete list)
		"""
		with h5py.File( self._h5_current_filename, 'r' ) as self._h5_current_file:	
			"""
			Control whether H5 file is a MuH5 file
			"""
			if not self._h5_current_file['muh5']:
				log.warning( f"{self._h5_current_file} seems not to be a MuH5 file: unrecognized format" )
				raise Mu32Exception( f"{self._h5_current_file} seems not to be a MuH5 file: unrecognized format" )

			"""
			get parameters values on H5 file
			"""
			group = self._h5_current_file['muh5']
			self._h5_parameters = dict( zip( group.attrs.keys(), group.attrs.values() ) )
			self._available_mems = self._h5_parameters['mems']
			self._pluggable_beams_number = int( len( self._available_mems ) / MU_BEAM_MEMS_NUMBER )	
			self.run_setargs( self._h5_run_kwargs )

			"""
			Perform controls on requested parameter values: see if they are in accordance with H5 file parameters
			"""
			error = False
			if self._sampling_frequency != self._h5_parameters['sampling_frequency']:
				error = MuException( f"MuH5: no available under/over sampling algorithm: requested sampling frequency of {self._sampling_frequency}Hz do not match recording one at {self._h5_parameters['sampling_frequency']}Hz" )
				log.error( str( error ) )
				raise error	

			if self._counter and not self._counter_skip and ( not self._h5_parameters['counter'] or ( self._h5_parameters['counter'] and self._h5_parameters['counter_skip'] ) ):
				error = MuException( f"MuH5: Counter is requested but not available on H5 data" )
				log.error( str( error ) )
				raise error	

			self._available_mems = list( self._h5_parameters['mems'] )
			if self._mems_number == 0:
				"""
				Check activated MEMs. 
				Beware that with MuH5, default activated MEMs (when not set by user) is 0 since we do not know the receiver type (Mu32, 256, 1024...)
				So if MEMs number is 0 -> set to available MEMs from H5 file
				"""
				self._mems = list( self._h5_parameters['mems'] )
				self._mems_number = len( self._mems )

			activated_mems = np.array( self._mems )
			mask = np.logical_not( np.isin( activated_mems , self._h5_parameters['mems'] ) )
			if len( activated_mems[mask] ) > 0:
				error = MuException( f"Some activated microphones ({activated_mems[mask]}) are not available on H5 file {self._h5_current_filename}. Available MEMs are: {self._h5_parameters['mems']} ")
				log.error( str( error ) )
				raise error	

			"""
			Start playing
			"""
			log.info( f" .Reading H5 file {self._h5_current_filename}")
			log.info( f" .{self._h5_parameters['duration']}s ({(self._h5_parameters['duration']/60):.02}min) of data in {self._h5_current_filename} H5 file" )
			log.info( f" .Available mems: {self._available_mems}" )
			log.info( f" .desired recording duration: {self._duration} s" )
			log.info( f" .minimal recording duration: {( self._transfers_count*self._buffer_length ) / self._sampling_frequency} s" )
			log.info( f" .{self._mems_number} activated microphones" )
			log.info( f" .activated microphones: {self._mems}" )
			log.info( f" .{self._analogs_number} activated analogic channels" )
			log.info( f" .activated analogic channels: {self._analogs }" )
			log.info( f" .whether counter is activated: {self._counter}" )
			log.info( f" .whether status is activated: {self._status}" )
			log.info( f" .total channels number is {self._channels_number}" )
			log.info( f" .datatype: {self._datatype}" )
			log.info( f" .number of USB transfer buffers: {self._buffers_number}" )
			log.info( f" .buffer length in samples number: {self._buffer_length} ({self._buffer_length*1000/self._sampling_frequency} ms duration)" )			
			log.info( f" .buffer length in 32 bits words number: {self._buffer_length}x{self._channels_number}={self._buffer_words_length} ({self._buffer_words_length*MU_TRANSFER_DATAWORDS_SIZE} bytes)" )
			log.info( f" .buffer duration in seconds: {self._buffer_duration}" )
			log.info( f" .minimal transfers count: {self._transfers_count}" )
			log.info( f" .multi-threading execution mode: {not self._block}" )
			log.info( f" .starting time: {self._h5_start_time * self._h5_parameters['duration'] / 100}s ({self._h5_start_time}% of file)" )

			"""
			Parameters
			----------
			* _h5_dataset_index: current dataset
			* _h5_dataset_index_ptr: current index in current dataset 
			* _counter_state: transfer buffer counting
			"""
			self._transfer_index = 0
			self._h5_playing = True
			skipping_counter = self._h5_parameters['counter'] and not self._h5_parameters['counter_skip'] and self._counter_skip
			start_time = self._h5_start_time * self._h5_parameters['duration'] / 100

			if start_time > 0:
				"""
				Start from requested starting time
				"""
				if start_time > self._h5_parameters['duration']:
					log.errort( f"Cannot read file at {start_time}s star time. File duration ({self._h5_parameters['duration']}) is too short" )
					raise MuException( f"Cannot read file at {start_time}s star time. File duration ({self._h5_parameters['duration']}) is too short" )

				self._h5_dataset_index = int( ( start_time * self._sampling_frequency ) // self._h5_parameters['dataset_length'] )
				self._h5_dataset_index_ptr = int( ( start_time * self._sampling_frequency ) % self._h5_parameters['dataset_length'] )
			else:
				"""
				Start from beginning
				"""
				self._h5_dataset_index = 0
				self._h5_dataset_index_ptr = 0

			dataset = self._h5_current_file['muh5/' + str( self._h5_dataset_index ) + '/sig']
			if skipping_counter:
				transfer_buffer = np.array( dataset[:] )[1:self._h5_parameters['channels_number'],:]
			else:
				transfer_buffer = np.array( dataset[:] )

			while self._h5_playing == True:

				if self._h5_dataset_index_ptr + self._buffer_length <= self._h5_parameters['dataset_length']:
					"""
					There is enough data in current dataset: put in the queue
					"""
					self._signal_q.put( transfer_buffer[:,self._h5_dataset_index_ptr:self._h5_dataset_index_ptr+self._buffer_length] )
					self._h5_dataset_index_ptr += self._buffer_length
				else:
					"""
					No enough data in current dataset: open next dataset
					"""
					if self._h5_dataset_index < self._h5_parameters['dataset_number']:
						"""
						Next dataset exists: get last data of current dataset, open next and complete buffer
						"""
						current_dataset_last_samples_number = self._h5_parameters['dataset_length'] - self._h5_dataset_index_ptr
						buffer = transfer_buffer[:,self._h5_dataset_index_ptr:self._h5_dataset_index_ptr+self._h5_parameters['dataset_length']]
						dataset = self._h5_current_file['muh5/' + str( self._h5_dataset_index ) + '/sig']
						if skipping_counter:
							transfer_buffer = np.array( dataset[:] )[1:self._h5_parameters['channels_number'],:]
						else:
							transfer_buffer = np.array( dataset[:] )

						new_dataset_first_samples_number = self._buffer_length - current_dataset_last_samples_number
						buffer = np.append( buffer, transfer_buffer[:,:new_dataset_first_samples_number], axis=1 )
						self._signal_q.put( buffer )
						self._h5_dataset_index_ptr = new_dataset_first_samples_number
						self._h5_dataset_index += 1
						log.info( f" .new dataset: [{self._h5_dataset_index}]" )
					else:
						"""
						No more dataset: save current buffer and stop playing
						"""
						buffer = transfer_buffer[:,self._h5_dataset_index_ptr:self._h5_parameters['dataset_length']]
						buffer = np.append( buffer, np.zeros( (self._mems_number, self._buffer_length - self._h5_parameters['dataset_length'] + self._h5_dataset_index_ptr), dtype=np.int32), axis=1 )
						self._signal_q.put( buffer )
						self._h5_playing = False
						log.info( f" .no more dataset: stop playing" )


				self._transfer_index += 1
				if self._transfers_count != 0 and  self._transfer_index >= self._transfers_count:
					self._h5_playing = False

				"""
				Wait for real time: emit signal through the net to time interval equal to the buffer transfer duration
				Should be improved by using time event emetter
				"""
				sleep( self._buffer_duration )

			"""
			Call the final callback user function if any 
			"""
			if self._post_callback_fn != None:
				self._post_callback_fn( self )




	def wait( self ):
		"""
		wait for thread termination (blocking call)
		"""
		if self._block:
			log.warning( "wait() should not be used in blocking mode" )
			return

		self._h5_ctrl_thread.join()
		if self._h5_ctrl_thread_exception:
			raise self._h5_ctrl_thread_exception


	def is_alive( self ):
		"""
		chack if thread is always running (non blocking call)
		"""
		if self._block:
			log.warning( "is_alive() should not be used in blocking mode" )
			return
		
		return self._h5_ctrl_thread.is_alive()


	def stop( self ):
		"""
		Stop the transfer loop
		"""
		self._h5_playing = False




def main():

	#muH5 = MuH5( 'mu5h-20220507-224200.h5' )
	muH5 = MuH5( 'mu5h-20220507-224200.h5' )
	
	muH5.run(
		duration=2
	)

if __name__ == "__main__":
	main()


#a = [ -3502.,  -3232.,  -6190.,  -6946.,  -6288.,  -7560.,  -7486.,  -6848.,  -3712., -3680.,  -2686.,  -2386.,   2296.,   5658.,   7584.,   9784.,   9208.,   9952., 6452.,   7018.,   5696.,   7590.,   4884.,   8022.,  11706.,  12034.,  14892., 15728.,  16466.,  17300.,  18816.,  16344.,  14904.,  13798.,  10414.,   6474., 6290.,   5226.,   8388.,   9272.,   8160.,  10264.,  12090.,  14362.,  14836., 21114.,  19828.,  19636.,  20940.,  20466.,  18298.,  17896.,  16010.,  12304., 14026.,  15140.,  17568.,  18378.,  17862.,  19724.,  17998.,  15140.,  11330., 8896.,   6768.,   4826.,    538.,  -3434.,  -2524.,  -2586.,   -754.,   -204., 528.,   -458.,  -3170.,  -4910.,  -5704., -11032., -14548., -15818., -15354., -16076., -17686., -20104., -20544., -17654., -18202., -17742., -15812., -13654., -14220., -14936., -16452., -18112., -18248., -17542., -19752., -18144., -19196., -17632.]