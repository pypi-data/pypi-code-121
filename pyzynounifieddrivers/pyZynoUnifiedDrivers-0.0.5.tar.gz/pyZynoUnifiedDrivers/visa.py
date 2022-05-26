'''
Zyno Medical Virtual Instrument Software Architecture (VSIA) python library
Created on May 13, 2022

@author: Yancen Li
'''
import sys
import platform
import serial
from pyZynoUnifiedDrivers.module_miva import SerialComm


class ResourceManager:
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass
    
    def list_resources(self):
        '''Scan Serial Port'''
        ports = []
        if platform.system() == 'Linux':
            ports = ['/dev/ttyUSB%s' % (i) for i in range(0, 256)]
        else:
            ports = ['com%s' % (i) for i in range(1, 256)]
        result = []
        for port in ports:
            try:
                ser = serial.Serial(port)
                ser.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        result = tuple(result)
        return result

    def open_resource(self, serial_port):
        '''
        Open Resource
        '''
        return SerialComm(serial_port)


def main(argv):
    '''main function'''
    rm = ResourceManager()
    miva = rm.open_resource('com5')
    # Test [query] Function
    pump_sn = miva.query(':serial?')
    print(pump_sn)
    # Test [write] Function
    miva.write(':serial?')
    # Test [read] Function
    pump_sn = miva.read()
    print('len(pump_sn) = {}'.format(len(pump_sn)))
    print(pump_sn)
    # Test [*idn] query
    pump_identifier = miva.query('*idn?')
    print(pump_identifier)
    # Test [close] function of miva class
    miva.close()
    # Test [list_resources] Function
    resources = rm.list_resources()
    print(resources)


if __name__ == "__main__":
    main(sys.argv)
