import string
import random


def get_code(length = 6):
    # length of the string.
    S = length  
    # call random.choices() string module to find the string in Uppercase + numeric data.  
    ran = ''.join(random.choices(string.ascii_uppercase + string.digits, k = S)) 

    return ran