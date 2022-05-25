import enum
import os.path
import os
import json

class PinData():
  pinNumber = 0
  mode = 0
  request = 0
  moduleCount = 0
  minPulse = 0
  maxPulse = 0

class RGBLedData():
  pinNumber = 0
  red = 0
  green = 0
  blue = 0
  brightness = 100
  prevBrightness = 0

class ProtocolData():
  def __init__(self) -> None:
    self.data = []
    self.delay = 0.0

class GyroData():
  def __init__(self) ->None:
    self.angleX = 0
    self.angleY = 0
    self.angleZ = 0
    self.gyroX = 0
    self.gyroY = 0
    self.gyroZ = 0
    self.shake = 0

class RotaryPostionData():
  def __init__(self)->None:
    self.points = []
    self.firstValue = None
    self.rotation = 0
    self.position = 0
    self.calibration = 0
    self.enable = False  

class Notes(enum.Enum):
  C1  = 33
  CS1 = 35
  D1  = 37
  DS1 = 39
  E1  = 41
  F1  = 44
  FS1 = 46
  G1  = 49
  GS1 = 52
  A1  = 55
  AS1 = 58
  B1  = 62

  C2  = 65
  CS2 = 69
  D2  = 73
  DS2 = 78
  E2  = 82
  F2  = 87
  FS2 = 93
  G2  = 98
  GS2 = 104
  A2  = 110
  AS2 = 117
  B2  = 123

  C3  = 131
  CS3 = 139
  D3  = 147
  DS3 = 156
  E3  = 165
  F3  = 175
  FS3 = 185
  G3  = 196
  GS3 = 208
  A3  = 220
  AS3 = 233
  B3  = 247   

  C4  = 262    
  CS4 = 277
  D4  = 294
  DS4 = 311
  E4  = 330
  F4  = 349
  FS4 = 370
  G4  = 392
  GS4 = 415
  A4  = 440
  AS4 = 466
  B4  = 494   

  C5  = 523    
  CS5 = 554
  D5  = 587    
  DS5 = 622
  E5  = 659    
  F5  = 698    
  FS5 = 740
  G5  = 784    
  GS5 = 831
  A5  = 880    
  AS5 = 932
  B5  = 988    

  C6  = 1047   
  CS6 = 1109
  D6  = 1175
  DS6 = 1245
  E6  = 1319
  F6  = 1397
  FS6 = 1480
  G6  = 1568
  GS6 = 1661
  A6  = 1760
  AS6 = 1865
  B6  = 1976

  C7  = 2093   # 도
  CS7 = 2217
  D7  = 2349   # 레
  DS7 = 2489
  E7  = 2637   # 미
  F7  = 2794   # 파
  FS7 = 2960
  G7  = 3136   # 솔
  GS7 = 3322
  A7  = 3520   # 라
  AS7 = 3729
  B7  = 3951   # 시

  C8  = 4186   # 도
  CS8 = 4435
  D8  = 4699
  DS8 = 4978
  E8  = 5274
  F8  = 5588
  FS8 = 5920
  G8  = 6272
  GS8 = 6645
  A8  = 7040
  AS8 = 7459
  B8  = 7902
    
class RobokitRS_config():
  def readConfigFile(self, config_path, pins):
    print(config_path)
    if config_path.isspace():
      print("Pin configuration error : Empty dir")
      return

    if not os.path.isdir(config_path):
      print("Pin configuration error : Not dir")
      return

    if not os.path.isfile(config_path + "/pins.config"):
      print("Pin configuration error : config file not exist")
      return

    self.jsonParser(config_path, pins)

  def jsonParser(self, config_path, pins):
    f = open(config_path + "/pins.config", 'r')
    configDatas = json.loads(f.read())
    pindatas = configDatas.get('pins')

    if pindatas is None:
      print("Pin configuration error : file error")
      return

    for data in pindatas:
      pin = PinData()
      
      pinnum = data.get('number')
      if pinnum is None:
        print("Pin configuration error : file syntax error")
        return
      pin.pinNumber = pinnum
      
      mode = data.get('mode')
      if mode is None:
        print("Pin configuration error : file syntax error")
        return
      pin.mode = mode

      pins[pinnum] = pin

  def __init__(self):
    pass