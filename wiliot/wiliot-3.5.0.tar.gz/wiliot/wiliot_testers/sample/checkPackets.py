'''
Created on Jan 5, 2022

@author: davidd
'''
from sys import path, exit
from os.path import exists, isfile, abspath, dirname, join, isdir, basename
path.append(abspath(dirname(join('..', '..', '..', '..', 'pywiliot_internal'))))
from pywiliot_internal.wiliot.packet_data_tools.process_encrypted_packets import estimate_diff_packet_time

if __name__ == '__main__':
    packets = ['process_packet("03B4C1CD11371E16AF0502000089E3C791F1B3EBFA732AD5EED8918AD17B9A0354219044713D9957")']
    packetsTimes = [54.92031]
    print(estimate_diff_packet_time(packets, packetsTimes))
