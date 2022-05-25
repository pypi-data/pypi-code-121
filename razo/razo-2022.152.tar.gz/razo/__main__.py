# coding=utf-8
import datetime
import os
import sys
import time as tm

import numpy as np
import password as pw
try:
    env = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH'] + '\\.razodata\\'
except KeyError as fru:
    env = os.environ['HOME'] + '/.razodata/'

try:
    from langpack import pack
except ModuleNotFoundError as aheddew:
    from langpack_d import pack
vers = ['2022.152', 'os_3']


class razo_p:
    password = pw.Password(method='sha512', hash_encoding='base64')

read1=''
read2=''

rooting = False
sudoroot = False
nowsudo = False

try:
    if sys.argv[1] == '-root':
        rooting = True
except IndexError as inddde:
    rooting = False
liense = pack[0]


def __etting__():
    ld = []
    ld2 = []
    print(pack[1])
    print(liense)
    a = input(pack[2])
    if a == 'n':
        print(pack[3])
        tm.sleep(5)
        sys.exit(0)
    print(pack[4])
    a = input('\033[0;30;40m')
    print('\033[0;37;40m')
    c = razo_p()
    c.password = a
    np.save(env + 'passw.npy', c)
    a = input(pack[5])
    np.save(env + 'usern.npy', a)


def showinfo():
    listget = pack[13]
    timer = datetime.datetime.now()
    weekday = listget[timer.weekday()]
    print(timer.strftime(pack[14]) + ' {}'.format(weekday))
    print('Razo {0}({1})'.format(vers[0], vers[1]))
    print(pack[6])


h = pack[8]


def sc():
    global sudoroot
    if not sudoroot:
        a = input(pack[9] + '\033[8;37;40m')
        print('\033[8;37;40m')
        if read1.password == a:
            sudoroot = True
            return True
        else:
            print(pack[18])
            return False
    else:
        return True


def help():
    print(h)


def su():
    global rooting
    if rooting:
        return 0
    a = input(pack[9] + '\033[8;37;40m')
    print('\033[0;37;40m')
    if read1.password == a:
        rooting = True
    else:
        tm.sleep(2)
        print(pack[10])


def shutdown():
    if rooting:
        yes = input(pack[11])
        if yes == 'y':
            print(pack[12])
            tm.sleep(5)
            sys.exit(0)


def setting():
    global rooting
    if rooting:
        __etting__()
        rooting = False
    else:
        print(pack[15])


def time():
    listget = pack[13]
    timer = datetime.datetime.now()
    weekday = listget[timer.weekday()]
    print(timer.strftime(pack[14]) + ' {}'.format(weekday))


def info():
    showinfo()


def __wai__(a):
    global nowsudo
    if a == 'exit':
        print('No way!')
        return 0
    try:
        exec(a + '()')
    except (SyntaxError, NameError, TypeError) as abcddd:
        if a.split(' ')[0] == 'sudo':
            sc()
            try:
                exec(a.split(" ")[1] + '()')
            except (SyntaxError, NameError) as abcdde:
                try:
                    dc = os.system(a)
                    tm.sleep(0.5)
                    print(pack[20].format(dc))
                except SystemExit as fhuuuifr:
                    pass
        else:
            try:
                dc = os.system(a)
                tm.sleep(0.5)
                print(pack[20].format(dc))
            except SystemExit as fhuuuifr:
                pass


def __main_p__():
    while True:
        if rooting:
            a = input('[root]>>> ')
        else:
            a = input('[user]>>> ')
        __wai__(a)


def getin():
    global read1
    global read2
    if not os.path.exists(env):
        os.mkdir(env)
        __etting__()
    try:
        read1 = np.load(env + 'passw.npy', allow_pickle=True).item()
        read2 = np.load(env + 'usern.npy', allow_pickle=True).item()
    except FileNotFoundError as nots:
        __etting__()
    showinfo()
    print(pack[17].format(read2))
    __main_p__()


if __name__ == '__main__':
    getin()
