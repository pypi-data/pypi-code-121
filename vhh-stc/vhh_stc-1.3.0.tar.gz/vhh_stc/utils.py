import sys
import os
import numpy as np
from matplotlib import pyplot as plt
plt.rc('pdf', fonttype=42)


class STDOUT_TYPE:
    INFO = 1
    ERROR = 2

def printCustom(msg: str, type: int):
    if(type == 1):
        print("INFO: " + msg);
    elif(type == 2):
        print("ERROR: " + msg);
    else:
        print("FATAL ERROR: stdout type does not exist!")
        exit();


def getCommandLineParams():
    printCustom("read commandline arguments ... ", STDOUT_TYPE.INFO)
    number_of_args = len(sys.argv);
    print('Number of arguments:', len(sys.argv), 'arguments.')
    print('Argument List:', str(sys.argv))

    if (number_of_args < 3):
        printCustom("There must be at least two commandline argument(s)", STDOUT_TYPE.ERROR)
        exit()

    params = sys.argv;
    print(params)
    return params;


def createFolder(path):
    if not os.path.exists(path):
        print("create folder " + str(path))
        os.mkdir(path)
    else:
        print("folder already exsists - [" + str(path) + "]")


def csvWriter(dst_folder="", name="metrics_history.log", entries_list=None):
    if (entries_list == None):
        print("ERROR: entries_list must have a valid entry!")

    # prepare entry_line
    entry_line = ""
    for i in range(0, len(entries_list)):
        tmp = entries_list[i]
        entry_line = entry_line + ";" + str(tmp)

    fp = open(dst_folder + "/" + str(name), 'a')
    fp.write(entry_line + "\n")
    fp.close()


def csvReader(name="metrics_history.log"):
    #print(name)
    fp = open(name, 'r')
    lines = fp.readlines()
    fp.close()

    entries_l = []
    for line in lines:
        line = line.replace('\n', '')
        line = line.replace('', '')
        #print(line)
        line_split = line.split(';')

        tmp_l = []
        for split in line_split[:-1]:
            tmp_l.append(split)
        #print(tmp_l)
        entries_l.append(tmp_l)

    entries_np = np.array(entries_l)
    return entries_np


def plotClassDistribution(file_name="class_distr", file_extension="pdf", class_distr_name=[], class_distr_data=[]):
    plt.figure()
    y_pos = np.arange(len(class_distr_data))
    plt.bar(y_pos, class_distr_data, align='center', alpha=0.5)
    plt.xticks(y_pos, class_distr_name)
    plt.ylabel('number of frames')
    plt.title('Class Distribution per Shot')
    plt.savefig(file_name + "." + file_extension, dpi=500)
