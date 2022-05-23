from uncertainties import ufloat
from uncertainties.umath import *


def printp(x, txt=None, txtxt=None, num=2):  # 이쁘게 출력해준다.
    temp = '{:.' + str(num) + 'uP}'
    if txt is None:
        txt = ''
    else:
        txt = str(txt)
    if txtxt is None:
        txtxt = ''
    else:
        txtxt = str(txtxt)
    print(txt + temp.format(x) + txtxt)


def printp_list(X, txt=None, txtxt=None, num=2):  # 리스트를 이쁘게 출력해준다. 한 줄에 한 원소.
    for x in X:
        printp(x, txt=txt, txtxt=txtxt, num=num)


def printp_list_oneline(x, txt='[', txtxt=']', num=2):  # 리스트를 이쁘게 출력해준다. 한 줄에 다 출력한다.
    n = len(x)
    temp = '{:.' + str(num) + 'uP}'

    if txt is None:
        txt = ''
    else:
        txt = str(txt)
    if txtxt is None:
        txtxt = ''
    else:
        txtxt = str(txtxt)

    print(txt, end = '')
    i = 0
    while i < n:
        if i == n-1:
            END = ''
        else:
            END = ', '
        print(temp.format(X[i]), end = END)
        i = i+1
    print(txtxt, end = '\n')