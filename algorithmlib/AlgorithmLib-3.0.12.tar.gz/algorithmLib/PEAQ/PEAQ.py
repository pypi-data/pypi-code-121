import os
import sys


def cal_peaq(ref, est):
    '''
    :param ref:
    :param est:
    :return:
    '''
    cmd = sys.prefix + '/peaqb.exe -r '+ ref + ' -t ' + est
    result = os.popen(cmd)
    res = result.read()
    for line in res.splitlines():
        print(line)

if __name__ == '__main__':
    cal_peaq('eval1.wav','eval1_echo100.wav')