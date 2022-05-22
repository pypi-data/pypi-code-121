import time
def fps():
  fs = 0
  start = time.time()
  while True:
    fs+=1
    end = time.time()
    if end-start >= 1:
      return fs
      break