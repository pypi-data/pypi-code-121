from datetime import datetime, timezone, timedelta


def timestamp():
    t=datetime.now(timezone.utc)
    x=datetime.timestamp(t)-12*3600
    x=round(x)
    return x



if __name__ == '__main__':
    print(timestamp())


