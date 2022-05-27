import datetime
import math
import random
import numpy
import uuid
import re
import requests
import json
class Random_decimal:
  def getProbability(nl:bool=False):
    try:
      time = datetime.datetime.now()
      timeH = time.hour
      timeM = time.minute
      timeS = time.second
      timeL = timeH*3600+timeM*60+timeS
      sc = random.uniform(timeM, timeS)
      while sc > 1:
        sc = sc/timeH
      pl = numpy.random.binomial(timeL, sc, 1)
      uuidc = str(uuid.uuid4())
      suid = uuidc.replace("-", "")
      UUIDINT = int(re.sub(r"[A-Za-z]","",suid))
      b = []
      for i in str(UUIDINT):
        b.append(int(i))
      if b[timeH - 4] <= 5:
        (UUIDINT) = int((int(UUIDINT) - int(timeL)) / int(timeL) - int(pl[0]))
      else:
        (UUIDINT) = int(int(UUIDINT) / int(timeL))
      cityID = ["101021300","101030100","101030200","101030300","101030400","101030500","101030600","101030700","101030800","101030900","101031000","101031100","101031200","101031300","101031400","101040100","101040200","101040300","101040400","101040500","101040600","101040700","101040800","101040900","101041000","101041100","101041200","101041300","101041400","101041500","101041600","101041700","101041800","101041900","101042000","101042100","101042200","101042300","101042400","101042500","101042600","101042700","101042800","101042900","101043000","101043100","101043200","101043300","101043400","101043500","101043600","101043700"]
      city = random.sample(cityID, 1)
      wt = requests.get('http://www.weather.com.cn/data/sk/{city}.html'.format(city=city[0]))
      wt.encoding='utf-8'
      wt = json.loads(wt.text)
      if wt['weatherinfo']['temp'] != "暂无实况":
        UUIDINT = UUIDINT * float(wt['weatherinfo']['temp'])
      else:
        Random_decimal.getProbability()
      if len(str(UUIDINT)) >= 9:
        vbl = int(str(len(str(UUIDINT)) - 8))
        UUIDINT = str(UUIDINT)[:-vbl]
      elif len(str(UUIDINT)) <= 10:
          for i in list(range(0, 10 - len(str(UUIDINT)))):
              ddf = str(random.randint(1, 9))
              UUIDINT = str(UUIDINT).join(ddf)
      else:
        ...
      try:
        if int(UUIDINT) > 10:
          ...
        else:
          ...
      except:
          UUIDINT = float(UUIDINT) - math.floor(float(UUIDINT))
          if len(str(UUIDINT)) >= 11:
            vbl = int(str(len(str(UUIDINT)) - 10))
            UUIDINT = str(UUIDINT)[:-vbl]
          elif len(str(UUIDINT)) <= 10:
              for i in list(range(1, 10 - len(str(UUIDINT)))):
                  ddf = str(random.randint(1, 9))
                  km = str("".join(ddf))
                  UUIDINT = str(UUIDINT).replace("00", km)
          if str(UUIDINT)[-2:] == "99" or str(UUIDINT)[-2:] == "00":
            if str(UUIDINT)[-2:] == "99":
              for i in [1, 2]:
                bn = str(random.randint(0, 9))
                km = str("".join(bn))
              UUIDINT = str(UUIDINT).replace("99", km)
            if str(UUIDINT)[-2:] == "00":
              for i in [1, 2]:
                bn = str(random.randint(0, 9))
                km = "".join(bn)
              UUIDINT = str(UUIDINT).replace("00", km)
          else:
            ...
          # if len(str(UUIDINT)) <= 8:
          #     for i in list(range(1, 9 - len(str(UUIDINT)))):
          #         ddf = str(random.randint(1, 9))
          #         UUIDINT = str(str(UUIDINT).join(ddf))
          # else:
          #   ...
          if UUIDINT not in list(range(0, 11)) or UUIDINT != "0." or UUIDINT < 1:
            if nl == True:
              print(UUIDINT)
              return UUIDINT
            else:
              return UUIDINT
          else:
            Random_decimal.getProbability()
    except:
      Random_decimal.getProbability()