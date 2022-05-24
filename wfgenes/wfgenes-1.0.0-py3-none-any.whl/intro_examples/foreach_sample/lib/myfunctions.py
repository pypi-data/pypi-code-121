#from parsl import python_app
import time
import yaml


#@python_app
def data_generator(list_length):
    # Generate and initialize list 
    data = [0 for i in range(list_length)]
    for i in range(list_length):
        data[i]= i +1
        with open('data.yaml', 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
    return data    


#@python_app
def plus_minus(x, y):
    """ x - a list, y - a number """
    return_list_x = []
    return_list_y = []
    for i in x:
        return_list_x.append(i + y )
        return_list_y.append(i - y )
        time.sleep(1)
    return return_list_x, return_list_y

#@python_app
def sum_square(x, y, z):
    """ x, y - lists of same length, z - a number """
    return_list = []
    for i, j in zip(x, y):
        return_list.append(z*(i**2+j**2))
        time.sleep(1)
    return return_list

#@python_app
def average_list(x):
    """ x, y - lists of same length, z - a number """
    total_sum = 0
    for i in x:
        total_sum = total_sum + i
    return [total_sum / len(x)]    

if __name__ == '__main__':
    data = [1, 2, 3, 4]
    datax, datay = plus_minus(data, 1)
    results = sum_square(datax, datay, 2)
    print(results)
