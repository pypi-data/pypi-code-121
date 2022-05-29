from datetime import datetime as dt
from time import strftime, localtime
f = lambda: dt.now().year
t = lambda: int(strftime("%Y", localtime())) == f()