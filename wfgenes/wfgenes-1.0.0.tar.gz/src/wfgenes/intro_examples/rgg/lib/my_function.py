#from parsl import python_app
import time


#@python_app
def weighted_sleep(*args, **kwargs):
    if 'len_output' in kwargs:
        output_number = kwargs['len_output']
    else:
        output_number = 1
    if 'sleep_time' in kwargs:    
        sleep_time = kwargs['sleep_time']
    else:
        sleep_time = 1 
    id =  kwargs['id'] 
    #print('Node', id,' is Sleeping for', sleep_time, "seconds.")
    time.sleep(int(sleep_time))
    output_list = ['Null' for y in range(int(output_number))]
    return output_list
