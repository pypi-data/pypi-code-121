# mu32wsh5play.py python program example for MegaMicro Mu32 receiver 
#
# Copyright (c) 2022 DistalSense
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
Run the Mu32 remote receiver during some seconds as H5 player

Documentation is available on https://beameo.io

Please, note that the following packages should be installed before using this program:
	> pip install libusb1
	> pip install matplotlib
"""

welcome_msg = '-'*20 + '\n' + 'Mu32 run program\n \
Copyright (C) 2022  distalsense\n \
This program comes with ABSOLUTELY NO WARRANTY; for details see the source code\'.\n \
This is free software, and you are welcome to redistribute it\n \
under certain conditions; see the source code for details.\n' + '-'*20

import argparse
import numpy as np
import queue
import matplotlib.pyplot as plt
from mu32.core import logging, Mu32ws, log

MEMS = (0, 1, 2, 3, 4, 5, 6, 7)
DURATION = 1
DEFAULT_IP = '127.0.0.1'
DEFAULT_PORT = 8002
DEFAULT_FILENAME = './'
DEFAULT_START_TIME = 0

log.setLevel( logging.INFO )

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument( "-d", "--dest", help=f"set the server network ip address. Default is {DEFAULT_IP}" )
    parser.add_argument( "-p", "--port", help=f"set the server listening port. Default is {DEFAULT_PORT}" )
    parser.add_argument( "-f", "--filename", help=f"set the server H5 filename or directory to play. Default is {DEFAULT_FILENAME}" )
    parser.add_argument( "-t", "--start", help=f"set the start time in seconds. Default is {DEFAULT_START_TIME}" )

    args = parser.parse_args()
    dest = DEFAULT_IP
    port = DEFAULT_PORT
    filename = DEFAULT_FILENAME
    start_time = DEFAULT_START_TIME
    if args.dest:
        dest = args.dest
    if args.port:
        port = args.port
    if args.filename:
        filename = args.filename
    if args.start:
        start_time = args.start

    print( welcome_msg )

    plt.ion()                               # Turn the interactive mode on.
    fig, axs = plt.subplots( len( MEMS ) )  # init figure with MEMS_NUMBER subplots
    fig.suptitle('Mems signals')

    try:
        mu32 = Mu32ws( remote_ip=dest, remote_port=port )
        mu32.run( 
            mems=MEMS,                      # activated MEMs
            duration=DURATION,              # ask for DURATION seconds acquisition
            system='MuH5',                  # set the server in play mode
            h5_play_filename=filename,      # visit the data directory of the server
            h5_start_time=start_time        # set the starting time to 0 second
        )

        plot_on_the_fly( mu32, axs )
        mu32.wait()
	
    except Exception as e:
        print( 'aborting: ', e )


def plot_on_the_fly( mu32, axs ):

	while True:
		"""
		get last queued signal and plot it
		"""
		try:
			data = mu32.signal_q.get( block=True, timeout=2 )
		except queue.Empty:
			break

		time = np.array( range( np.size( data, 1 ) ) )/mu32.sampling_frequency
		for s in range( mu32.mems_number ):
			axs[s].cla()
			axs[s].plot( time, data[s,:] * mu32.sensibility )
	
		plt.pause( 10e-4 )



if __name__ == "__main__":
	main()