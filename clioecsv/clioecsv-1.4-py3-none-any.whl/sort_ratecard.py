def is_included(first, second):
    """ this function to check if the first destination string is in the second destination string

    first(str): first destination string
    second(str): second destination string

    return bool
    """
    return first.upper() in second.upper()


def file_processing(file_name: str, output_file: str, dest_idx: int, prefix_idx: int, rate_idx: int, flag_indicator: str = "Destination"):
    """ this procedure is to prepare the pricing book for calculation script.

    parameters:
    file_name(str): file name of the supplied rate card csv book
    output_file(str): output file name 
    dest_idx(int): destination column index (start 0, 1 ..)
    prefix_idx(int): prefix column index (start 0, 1 ..)
    rate_idx(int): rate column index (start 0, 1 ..)
    flag_indicator(str): start processing after this line

    return output_file
    """
    flag = 0
    flag_indicator = flag_indicator

    file_as_list = []
    with open(file_name, "r") as file:
        for line in file:
            line = line.strip().split(",")

            if flag == 0:  # skip until flag_indicator
                if (line[0] == flag_indicator):
                    flag = 1
                continue

            file_as_list.append(line)

    file_as_list_group = []
    file_len = len(file_as_list)
    idx = 0

    while(idx < file_len - 1):
        temp_list = []
        temp_list.append(file_as_list[idx])

        rolling_idx = idx + 1

        while is_included(file_as_list[idx][0], file_as_list[rolling_idx][0]):
            temp_list.append(file_as_list[rolling_idx])
            if(rolling_idx == file_len - 1):  # last item
                break
            rolling_idx += 1

        file_as_list_group.append(temp_list)

        idx = rolling_idx

    # print("-- after --")
    # for line in file_as_list_group:
    #     print(line)

    output = []
    for line in file_as_list_group:
        temp_list = rearrange_list(line, dest_idx, prefix_idx, rate_idx)
        while(temp_list):
            output.append(temp_list.pop())

    # print("__________________________")
    # for line in output:
    #     print(line)

    with open(output_file, "w") as fw:
        for line in output:
            fw.write(",".join(str(item)for item in line) + "\n")


def rearrange_list(line: list, dest_idx: int, prefix_idx: int, rate_idx: int):
    """ rearrange the sub-list so the pricing is in the correct order more precision at the top

    parameters:
    line(list): list of related destination rate card pricing
    dest_idx(int): destination column index (start 0, 1 ..)
    prefix_idx(int): prefix column index (start 0, 1 ..)
    rate_idx(int): rate column index (start 0, 1 ..)

    return list in the correct arrangement
    """
    d = dest_idx
    p = prefix_idx
    r = rate_idx

    output = []
    idx = 0
    if(len(line) == 1):
        output.append([line[idx][d], f"^{line[idx][p]}", line[idx][r], ""])

    while(idx < len(line) - 1):
        next_idx = idx + 1
        if(len(line[idx][d]) < len(line[next_idx][d]) and line[idx][r] == line[next_idx][r]):  # 2 price
            dest_set = {f"{line[idx][d]}:{line[idx][p]}"}
            while(len(line[idx][d]) < len(line[next_idx][d]) and line[idx][r] == line[next_idx][r]):
                dest_set.add(f"{line[next_idx][d]}:{line[next_idx][p]}")
                if (next_idx == len(line) - 1):
                    break
                next_idx += 1
            # logic here
            output.append([line[idx][d], f"^{line[idx][p]}", line[idx][r], '|'.join([str(item) for item in dest_set])]) \

            idx = next_idx

        elif(len(line[idx][d]) == len(line[next_idx][d]) and line[idx][r] == line[next_idx][r]):
            dest_set = {line[idx][d]}
            prefix = f"^({line[idx][p]}"
            while(len(line[idx][d]) == len(line[next_idx][d]) and line[idx][r] == line[next_idx][r]):
                dest_set.add(line[idx][d])
                prefix += f"|{line[next_idx][p]}"
                if (next_idx == len(line) - 1):
                    break
                next_idx += 1
            # logic here
            prefix += ")"
            output.append(['|'.join([str(item) for item in dest_set]), prefix, line[idx][r], ""]) \

            idx = next_idx

        else:  # single
            output.append([line[idx][d], f"^{line[idx][p]}", line[idx][r], ""])

            idx = next_idx

    return output


"""
from datetime import datetime
## MAIN EXECUTION ##
dest_idx = 0  # destination
prefix_idx = 1  # prefix
rate_idx = 2  # rate
file_name = "input_data/Symbio_MVP_International_Standard_Rate_Card_S3T0322.csv"
output_file = f"output_data/{datetime.now().strftime('%Y%m')}_{file_name.split('/')[1]}"
file_processing(file_name, output_file, dest_idx, prefix_idx, rate_idx)
"""
