import math, socket, time, os
def add(x, y):
  return x + y
def sub(x, y):
  return x - y
def mul(x, y):
  return x*y
def div(x, y):
  return x/y
def power(y, z):
  return y**z 
def intdiv(x, y):
  return x//y
def modl(x, y):
  return x%y
def value(x, y):
  if x > y:
    return x
  elif x<y:
    return y
  elif x == y:
    return 'Same.'
  else:
    print('Not Found.')
def ip():
    print (socket.gethostbyname(socket.gethostname()))
def wait(nums):
  time.sleep(nums)
def libs():
    os.system("pip3 freeze > requirements.txt")
def osc(Command):
  os.system(f"{Command}")
def ls():
  return os.getcwd()
