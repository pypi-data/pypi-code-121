import time

def timestamp_print():
  print('\033[92m'+str(time.time()))
  
def timestamp():
  return time.time()

def format_time_a():
  return time.strftime("%H:%M:%S",time.localtime(timestamp()))
  