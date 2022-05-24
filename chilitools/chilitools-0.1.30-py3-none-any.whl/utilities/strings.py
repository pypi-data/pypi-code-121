from datetime import datetime

def currentDatetime() -> str:
  return datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
