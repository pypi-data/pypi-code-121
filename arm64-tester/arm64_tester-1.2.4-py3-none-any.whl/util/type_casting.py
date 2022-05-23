def cast_to_output(type, value):
    try:
        if type == 'integer':
            return int(value)
        elif type == 'float':
            return float(value)
        
        return value
    except:
        return value