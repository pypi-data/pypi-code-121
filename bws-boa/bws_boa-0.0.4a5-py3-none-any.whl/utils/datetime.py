import pytz

def change_timezone(dt, origin='America/Caracas', target='America/Bogota'):
    utc = pytz.timezone(origin)  
    tz = pytz.timezone(target) # timezone you want to convert to from UTC
    try:
        value = utc.localize(dt, is_dst=None).astimezone(pytz.utc)
    except ValueError:
        value = dt 
    local_dt = value.astimezone(tz)
    return local_dt