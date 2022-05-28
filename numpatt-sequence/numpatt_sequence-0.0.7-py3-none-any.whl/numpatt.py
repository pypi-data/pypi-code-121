def convert_str_float(str_list, sep):
    """ This function will convert string input of number sequence to a list;
    list: string input of number sequence
    sep: seperator to separate numbers in the sequence 
    """
    sep_list = list(str_list.split(sep))
    n_list = []
    for item in sep_list:
        if item != sep and item != "" and item != ".":
            try:
                n_list.append(float(item))
            except:
                print("Data type error")
                exit()
    return n_list


def check_list(pattern_list):
    """ This function will check if the count of the items >=2;
    to calculate the general term between two numbers
    """
    if (len(pattern_list)) >= 2:
        return True
    else:
        print("Need at least two numbers in a sequence")
        return False


def get_common_term(pattern_list):
    """ This function will check if difference in sequence is equal
    number_list = [3, 6, 9, . . . . n]
    diff = a2 - a1
    """
    if check_list(pattern_list):
        diff = [j - i for i, j in zip(pattern_list[:-1], pattern_list[1:])]
        if diff.count(diff[0]) == len(diff):
            return True
        else:
            print("Difference or common term in sequence is not equal")
            return False


def get_common_ratio(pattern_list):
    """ This function will check if difference (ratio) in sequence is equal
    number_list = [3, 6, 9, . . . . n]
    diff = a2 / a1
    """
    if check_list(pattern_list):
        diff = [j / i for i, j in zip(pattern_list[:-1], pattern_list[1:])]
        if diff.count(diff[0]) == len(diff):
            return True
        else:
            print("Difference or common ratio in sequence is not equal")
            return False


def common_difference(pattern_list, n):
    """ This function will get the common difference in Number patterns and general term in a list
    number_list = [3, 6, 9, . . . . n]
    nth = a + (n – 1)d
    """
    if get_common_term(pattern_list):
        num1, num2 = pattern_list[0], pattern_list[1]
        d = num2 - num1
        n_value = num1 + (n - 1) * d
        return n_value


def multi_difference(pattern_list, n):
    """ This function will get the multi difference in Number patterns and ratio in a list
    number_list = [3, 6, 9, . . . . n]
    nth = a + r**(n-1)
    """
    if get_common_ratio(pattern_list):
        num1, num2 = pattern_list[0], pattern_list[1]
        r = num2 / num1
        n_value = num1 * r ** (n - 1)
        return n_value


def classify_pattern(pattern_list):
    """ This function will try to identify the pattern has a common term or common ratio
    """
    if get_common_term(pattern_list):
        return 1
    elif get_common_ratio(pattern_list):
        return 2
    else:
        return False
