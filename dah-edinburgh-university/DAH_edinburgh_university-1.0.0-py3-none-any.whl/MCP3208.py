"""
Python Library for MCP3208 ADC using Raspberry Pi 3 Model B+

Version for Edinburgh DAH course, replacing webiopi library

Based on https://github.com/MomsFriendlyRobotCompany/mcp3208

"""

import spidev
import RPi.GPIO as GPIO

class MCP3208:
  """Python Library for MCP3208 ADC using Raspberry Pi 3 Model B+"""

  def __init__(self, chip=0, vref=3.3):
    """Initialise MCP3208 with an SPI chip number (0 or 1) and reference voltage"""

    # Reference voltage
    self.vref = vref
    self.doPrint = False

    # Use the spidev library for communication
    self.spi = spidev.SpiDev(0, 1)
    self.spi.max_speed_hz=1000000
    self.spi.mode = 0
    self.spi.lsbfirst = False
    #self.spi.cshigh = False

    # Use the GPIO library for chip select
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    if chip == 0:
      self.setCS( 8 )
    elif chip == 1:
      self.setCS( 7 )
    else:
      raise ValueError('MCP3208 says: Invalid chip chosen (' + str(chip) + ')! Options are 0 or 1')

  def __del__(self):

    self.close()

  def setCS(self, cs):
    """Set a custom GPIO pin to use as chip select"""

    if cs < 0 or cs > 27:
      raise ValueError('MCP3208 says: Invalid CS chosen (' + str(cs) + ')! Options are 0-27')

    self.cs = cs
    GPIO.setup(self.cs, GPIO.OUT)
    GPIO.output(self.cs, GPIO.HIGH)

  def printRawData(self, value):
    """Display all binary communication to and from the MCP3208"""

    self.doPrint = value

  def analogCount(self):
    """Return the number of ADC input pins"""

    return 8

  def analogResolution(self):
    """Return the ADC resolution"""

    return 12

  def analogMaximum(self):
    """Return the maximum value for an ADC measurement"""

    return 4095

  def analogReference(self):
    """Return the configured reference voltage"""

    return self.vref

  def analogRead(self, channel):
    """Make a single ADC measurement for a specific input pin (expressed as integer)"""

    if channel > 7 or channel < 0:
      raise ValueError('MCP3208 says: Invalid channel chosen (' + str(channel) +')! Options are 0-7')

    cmd = 128  # 1000 0000
    cmd += 64  # 1100 0000
    cmd += ((channel & 0x07) << 3)

    # Activate chip select
    GPIO.output(self.cs, GPIO.LOW)

    # Write command to MCP3208, read its response
    ret = self.spi.xfer2([cmd, 0x0, 0x0])

    # Deactivate chip select
    GPIO.output(self.cs, GPIO.HIGH)

    if self.doPrint:
      print( "to MCP3208: " + str( [cmd, 0x0, 0x0] ) )
      print( "from MCP3208: " + str( ret ) )

    # get the 12b out of the return
    val = (ret[0] & 0x01) << 11  # only B11 is here
    val |= ret[1] << 3           # B10:B3
    val |= ret[2] >> 5           # MSB has B2:B0 ... need to move down to LSB

    return (val & 0x0FFF)  # ensure we are only sending 12b

  def analogReadFloat(self, channel):
    """Make a single ADC measurement for a specific input pin (expressed as float)"""

    return float( self.analogRead( channel ) ) / float( self.analogMaximum() )

  def analogReadVolt(self, channel):
    """Make a single ADC measurement for a specific input pin (expressed as voltage)"""

    return self.vref * self.analogReadFloat( channel )

  def analogReadAll(self):
    """Make an ADC measurement for every input pin (expressed as integer)"""

    result = [0]*8
    for channel in range( self.analogCount() ):
      result[ channel ] = self.analogRead( channel )

    return result

  def analogReadAllFloat(self):
    """Make an ADC measurement for every input pin (expressed as float)"""

    result = [0]*8
    for channel in range( self.analogCount() ):
      result[ channel ] = self.analogReadFloat( channel )

    return result

  def analogReadAllVolt(self):
    """Make an ADC measurement for every input pin (expressed as voltage)"""

    result = [0]*8
    for channel in range( self.analogCount() ):
      result[ channel ] = self.analogReadVolt( channel )

    return result

  def close(self):
    """Disconnect communication with the MCP3208"""

    self.spi.close()

