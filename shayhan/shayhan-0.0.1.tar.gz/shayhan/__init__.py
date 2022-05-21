import numpy

def p(value, limit=5):
    """ This is function to print the type, shape, and value of a variable

    Args:
        value (any type): any type of variable
        limit (int, optional): The length of a variable. Defaults to 5.
    """
    
    if isinstance(value, (float, int, str,)):
        print("Type:", end=' ')
        print(type(value))
        print("Value:")
        print(value)
        
    elif isinstance(value, (list, dict, tuple, set)):
        print("Type:", end=' ')
        print(type(value))
        print("Lenth:", end=' ')
        print(len(value))
        print("Value")
        print(value[:limit])

    elif isinstance(value, (numpy.ndarray, numpy.generic)): #type(value)==numpy.ndarray:
        if value.ndim>1:
            print("Type:", end=' ')
            print(type(value))
            print("Shape:", end=' ')
            print(value.shape)
            print("Value:", end=' ')
            print(value[:limit,:limit])
        else:
            print("Type:", end=' ')
            print(type(value))
            print("Shape:", end=' ')
            print(value.shape)
            print("Value:", end=' ')
            print(value[:limit])
            
        