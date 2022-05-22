import os


def import_csv_as_list(filename, split_by=","):
    """ Import text or csv file with default seperator = ","

    parameters:
    file_name (str): The path to a text or csv file (string or raw string)
    split_by (str): The text file delimiter

    returns:
    list: The content of the text or csv file as list
    """
    read_lines = []
    with open(filename) as csv:
        for line in csv:
            read_lines.append(line.strip().split(split_by))
    return read_lines


def distinct_by_column(list, distinct_by_column=1):  # excel column start from 1
    """ Convert list into distinct record with default column 1 as key, ie. distinct_by_column(list, 1)

    parameters:
    list (list): The list of records ie: txt or csv file as a list
    distinct_by_column (int): column number for the distinct record with default column 1

    returns:
    dict_values: The distinct record return as dict_values (list)
    """
    dict = {}
    for line in list:
        dict[line[distinct_by_column-1]] = line
    return dict.values()


def distinct_by_columns(list, *distinct_by_columns):  # excel column start from 1
    """ Convert list into distinct record with multiple columns as key, ie. distinct_by_columns(list, 1, 2)

    parameters:
    list (list): The list of records ie: txt or csv file as a list
    *distinct_by_columns (int(s)): multiple columns as the distinct record's key

    returns:
    dict_values: The distinct record return as dict_values (list)
    """
    dict = {}
    for line in list:
        distinct_key = ""
        for column in distinct_by_columns:
            distinct_key += line[column-1]

        dict[distinct_key] = line
    return dict.values()


# combination of the above 2 functions, distinct_by_column(s) can be int or list
def distinct_list_bycolumns(list, distinct_by_columns):   # not tested
    """ Convert list into distinct record with default column 1 as key.
    ie.
    distinct_list_bycolumns(lines, 2)
    distinct_list_bycolumns(list, [1, 2])

    parameters:
    list (list): The list of records ie: txt or csv file as a list
    distinct_by_column(s) (int or list of integer): single or multiple columns as the distinct record's key

    returns:
    dict_values: The distinct record return as dict_values (list)
    """
    dict = {}
    if type(distinct_by_columns) == type([1, 2]):
        for line in list:
            distinct_key = ""
            for column in distinct_by_columns:
                distinct_key += line[column-1]
            dict[distinct_key] = line
    else:
        for line in list:
            dict[line[distinct_by_columns-1]] = line
    return dict.values()


def sort_list(list, by_column, descending=False):
    """ Sort list by a particular column number.
    Note that you can import your csv or text file using function import_csv_as_list(filename, split_by=",").

    parameters:
    list (list pointer): input data for data transformation
    by_column (int): column number where you want your list to be sorted
    descending (boolean): default is ascending order

    returns: void
    """
    list.sort(key=lambda item: item[by_column-1], reverse=descending)


def sorted_list(list, by_column, descending=False, header=True):
    """ Sort list by a particular column number.
    Note that you can import your csv or text file using function import_csv_as_list(filename, split_by=",").

    parameters:
    list (list): input data for data transformation
    by_column (int): column number where you want your list to be sorted
    descending (boolean): default is ascending order

    returns:
    list: sorted list
    """
    header_line = []
    if header:
        header_line = list[:1]
        list = list[1:]
    newlist = sorted(
        list, key=lambda item: item[by_column-1], reverse=descending)
    return header_line+newlist


def remove_blank_top(list, by_column):
    """ remove the blank line on the top, choose column number where the first non blank row of that column will be the header.
    Note that you can import your csv or text file using function import_csv_as_list(filename, split_by=",").

    parameters:
    list (list): input data for data transformation
    by_column (int): column number where the first non blank row of that column will be the header

    returns:
    list: the returned list with blank top removed
    """
    cur_row = 0
    while cur_row < len(list):
        if list[cur_row][by_column-1] == "":
            cur_row += 1
        else:
            break
    while (cur_row > 0):
        del list[cur_row - 1]
        cur_row -= 1
    return list


def remove_blank_bottom(list, by_column):
    """ Remove the bottom blank line of your text file, choose the column number where the first non blank row of that column will be the last row.
    Note that you can import your csv or text file using function import_csv_as_list(filename, split_by=",").

    parameters:
    list (list): input data for data transformation
    by_column (int): column number where you want your rows of data stop at.

    returns:
    list: the returned list with blank bottom removed
    """
    last_row = len(list) - 1
    while (last_row >= 0):
        if list[last_row][by_column-1] == "":
            del list[last_row]
            last_row -= 1
        else:
            break
    return list


def export_to_csv(list, file_name, split_by=','):
    """ Export list to text file with comma delimiter or default delimiter = ",".

    parameters:
    list (list): data to be exported
    file_name (str): the path to a text file (string or raw string)
    split_by (str) the delimiter for the text or csv file

    returns:
    csv or text file: the output can be .txt or .csv format depends on how you name your file_name parameter.
    """
    with open(file_name, "w") as fin:
        for line in list:
            fin.write(split_by.join(line) + "\n")


def append_file(master_file_name, file_source, remove_header_line_number=0, remove_bottom_line_number=0):
    """ Function to combine a file with existing master_file_name. ie.: append_file("data/master.csv, "data/today_file.csv").
    if master_file_name not exist, it will create the file with header as the first file_source open.

    parameters:
    master_file_name (str): the path and full name of master file name.
    file_source (str): the path and full name of the file to be added
    remove_header_line_number (int): how many header lines to skip
    remove_bottom_line_number (int): how many tail lines to skip

    returns: void
    """
    if os.path.exists(master_file_name):
        with open(master_file_name, "a") as wr:
            with open(file_source) as content:
                if content:
                    list_content = list(content)
                    last_line = len(list_content) - remove_bottom_line_number
                    wr.writelines(
                        list_content[remove_header_line_number:last_line])
    else:
        with open(master_file_name, "w") as wr:
            with open(file_source) as content:
                if content:
                    list_content = list(content)
                    last_line = len(list_content) - remove_bottom_line_number
                    # only remove tail and leave header as is
                    wr.writelines(list_content[:last_line])


def merge_files(merge_file_name, list_of_file_sources, write_mode="a", remove_header_line_number=0, remove_bottom_line_number=0):
    """ Function to merge list of files into 1 file. ie: merge_files(merge_file_name, ["data/file1", "data/file2"], "a", 1, 0) # Remove Header

    parameters:
    merge_file_name (str): the path and full name of the merge file name.
    list_of_file_sources (list): list of files that need to be combined
    write_mode (str): "w" for write and "a" for append existing file (Note: case sensitive)
    remove_header_line_number (int): how many header lines to skip
    remove_bottom_line_number (int): how many tail lines to skip

    return a combine text or csv file with file name as per the merge_file_name
    """
    with open(merge_file_name, write_mode) as wr:
        for file in list_of_file_sources:
            with open(file) as content:
                if content:
                    list_content = list(content)
                    last_line = len(list_content) - remove_bottom_line_number
                    wr.writelines(
                        list_content[remove_header_line_number:last_line])


def transpose(list_data):
    """ This function is to transpose the data from list of rows to list of columns

    parameters:
    list_data (list of list): list of rows as a list ie.:[['name', 'class', 'grade'], ['A', 'Green', 'Year 1'], ['B', 'Green', 'Year 1'], ['C', 'Green', 'Year 1']]

    return transposed list i.e [['name', 'A', 'B', 'C'], ['class', 'Green', 'Green', 'Green'], ['grade', 'Year 1', 'Year 1', 'Year 1']]
    """
    columns = []
    n = 0
    while n < len(list_data[0]):
        columns.append([item[n] for item in list_data])
        n += 1
    return columns


def append_column(list_data, new_column):
    """ This function is to append a new column to the existing data

    parameters:
    list_data (list of list): list of rows as a list ie.:[['name', 'class', 'grade'], ['A', 'Green', 'Year 1'], ['B', 'Green', 'Year 1'], ['C', 'Green', 'Year 1']]
    new_column (list): the new column to be added in a list with the same length as the current list_data ie. ['grade', 'A', 'B', 'A']

    return data as list of list data
    """
    columns = []
    n = 0
    while n < len(list_data[0]):  # columns number
        columns.append([item[n] for item in list_data])
        n += 1
    return [col for col in (zip(*columns,  new_column))]


def append_columns(list_data, new_columns):
    """ This function is to append new columns to the existing data

    parameters:
    list_data (list of list): list of rows as a list ie.:[['name', 'class', 'grade'], ['A', 'Green', 'Year 1'], ['B', 'Green', 'Year 1'], ['C', 'Green', 'Year 1']]
    new_columns (list of new columns): the new columns to be added in a list with the same length as the current list_data ie. [['subject', 'Math', 'English', 'Math'], ['grade', 'A', 'B', 'A']]

    return data as list of list data
    """
    """ This function is to append new columns to the existing data

    return data as list of list data
    """
    columns = []
    n = 0
    while n < len(list_data[0]):  # columns number
        columns.append([item[n] for item in list_data])
        n += 1
    return [col for col in (zip(*columns,  *new_columns))]


def split_file(input_file, max_rows, has_header=True):
    """ split file into smaller files with a defined max_rows

    input_file (file): original file to split
    max_rows (int): the number of max rows in the smaller file
    has_header (boolean): default as True means the file has header
    """
    file_no = 1
    row_no = 0 if has_header else 1
    with open(input_file, 'r')as fr:
        output_name = f"data/{os.path.basename(input_file).split('.')[0]}{str(file_no)}.csv"
        print(output_name)
        with open(output_name, 'w') as fw:
            for line in fr:
                if row_no == 0:
                    header = line
                    row_no += 1
                    continue

                if row_no == 1:
                    if has_header:
                        fw.write(header)
                    fw.write(line)
                    row_no += 1
                    continue

                fw.write(line)
                row_no += 1
                if row_no == max_rows + 1:  # adjust by adding 1
                    row_no = 1  # reset
                    file_no += 1
                    output_name = f"data/{os.path.basename(input_file).split('.')[0]}{str(file_no)}.csv"
                    print(output_name)
                    fw = open(output_name, 'w')


def get_header_idx(wanted_header, header):
    """
    parameters:
    header(list): original header of the file

    return column index as list ie. [0, 2, 4]
    """
    idx_list = []
    for header_line in wanted_header:
        for no in range(len(header)):
            if header_line.strip() == header[no].strip():
                idx_list.append(no)
    return idx_list


def list_with_chosen_columns(wanted_header: list, header_line_no: int, input_file: str, delimiter=","):
    """
    wanted_header(list): the header line name to keep
    header_line_no(int): the header line row number
    input_file(str): the input filename
    delimiter(str) with default comma delimiter

    return data with selected column as list
    """
    idx = 0
    with open(input_file, "r") as f:
        for line in f:
            idx += 1
            if(idx == header_line_no):
                header = line.split(delimiter)
                idx_list = get_header_idx(wanted_header, header)
            exit

    new_column = {}
    for idx in idx_list:  # create dictionary
        new_column[idx] = []

    with open(input_file, "r") as f:
        for line in f:
            row = line.split(delimiter)
            for idx in idx_list:
                new_column[idx].append(row[idx])

    data = []
    for k in new_column.keys():
        data.append(new_column[k])
    output_data = [row for row in zip(*data)]

    return output_data


def file_with_chosen_columns(wanted_header: list, header_line_no: int, input_file: str, output_file: str, delimiter=","):
    """
    wanted_header(list): the header line name to keep
    header_line_no(int): the header line row number
    input_file(str): the input filename
    output_file(str): the output filename
    delimiter(str) with default comma delimiter

    return new file with the given output_file name
    """
    output_data = list_with_chosen_columns(wanted_header, header_line_no, input_file, delimiter=",") \

    with open(output_file, "w") as fw:
        for line in output_data:
            fw.write(delimiter.join(line))
