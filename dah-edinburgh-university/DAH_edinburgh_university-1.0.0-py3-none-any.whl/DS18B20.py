"""
Python Library for DS18B20 temperature sensor using Raspberry Pi 3 Model B+

Version for Edinburgh DAH course, replacing webiopi library

"""

import os.path

class DS18B20:
  """Python Library for DS18B20 temperature sensor using Raspberry Pi 3 Model B+"""

  def __init__(self, address):
    """Initialise DS18B20 with a 1-wire address"""

    self.path = os.path.join( "/sys/bus/w1/devices", address, "w1_slave" )
    self.doPrint = False

    if not os.path.exists( self.path ):
      raise FileNotFoundError( "DS18B20 says: could not find sensor with address " + str(address) )

  def printRawData(self, value):
    """Display all raw data from the DS18B20"""

    self.doPrint = value

  def getCelsius(self):
    """Return the measured temperature in Celsius"""

    # Load the raw temperature data
    inputFile = open( self.path, "r" )

    # The file is two lines long, and we only care about the last one
    lineOne = inputFile.readline()
    inputData = inputFile.readline()

    if self.doPrint:
      print( "from DS18B20: " + lineOne.strip('\n') )
      print( "from DS18B20: " + inputData.strip('\n') )

    # The last 5 characters of the line contain the temperature information
    inputData = inputData[ len( inputData ) - 6 : ]

    # Convert the temperature information to a number (with correct magnitude)
    inputTemperature = float( inputData ) / 1000.0

    inputFile.close()
    return inputTemperature
