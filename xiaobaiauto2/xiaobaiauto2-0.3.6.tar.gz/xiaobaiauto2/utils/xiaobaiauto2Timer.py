#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'xiaobaiauto2Timer.py'
__create_time__ = '2020/7/20 21:13'

from os import chdir, path
from subprocess import Popen, PIPE
from threading import Thread
from tkinter import Tk, Label, Entry, Button, Frame, Listbox, Scrollbar, filedialog, END, LEFT, RIGHT, Y, StringVar
from tkinter.messagebox import showerror
from xiaobaiauto2.config.config import TIMERCONFIG
from datetime import datetime
from time import sleep

_timer = TIMERCONFIG()

IS_RUN = False

root = Tk()
root.geometry(_timer.geometry)
root.title(_timer.timerTitle)
root.iconbitmap(_timer.timerpath)

_t = StringVar()
_t.set('* * * * *')
_p = StringVar()
_p.set(path.abspath(path.curdir))
_c = StringVar()
_c.set('pytest --html=report.html --self-contained-html')

def _jiexi(_type='min', _timer='* * * * *'):
    msg = '''
        范围：
        min     0 ... 59
        hour    0 ... 23
        day     1 ... 31
        mou     1 ... 12
        week    1 ... 7
        表达式：
        * or 1,2,3-7/2 or 1-7/2 or 1,2,3-7 or */2 or 1-7 or 1,2,3 or 1
    '''
    _min = list(range(60))
    _hour = list(range(24))
    _day = list(range(1, 32))
    _mou = list(range(1, 13))
    _week = list(range(1, 8))
    _data = {
        'min': _min,
        'hour': _hour,
        'day': _day,
        'mou': _mou,
        'week': _week
    }
    if '*' == _timer:
        return _data[_type]
    elif '-' in _timer and '/' in _timer and ',' in _timer:
        '''1,2,3-7/2'''
        _tmp = []
        for t in _timer.split(','):
            if '-' not in t and '/' not in t:
                _tmp.append(t)
            else:
                _tmp += list(range(int(t.split('/')[0].split('-')[0]),
                                   int(t.split('/')[0].split('-')[1]) + 1,
                                   int(t.split('/')[1])))
        _tmp = list(map(lambda x: int(x), _tmp))
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    elif '-' in _timer and '/' in _timer and ',' not in _timer:
        '''1-7/2'''
        _tmp = list(range(int(_timer.split('/')[0].split('-')[0]),
                          int(_timer.split('/')[0].split('-')[1]) + 1,
                          int(_timer.split('/')[1])))
        _tmp = list(map(lambda x: int(x), _tmp))
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    elif ',' in _timer and '-' in _timer and '/' not in _timer:
        '''1,2,3-7'''
        _tmp = []
        for t in _timer.split(','):
            if '-' not in t:
                _tmp.append(t)
            else:
                _tmp += list(range(int(t.split('-')[0]),
                                   int(t.split('-')[1]) + 1))
        _tmp = list(map(lambda x: int(x), _tmp))
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    elif ',' not in _timer and '-' not in _timer and '/' in _timer:
        '''*/2'''
        _tmp = []
        if '*' == _timer.split('/')[0]:
            return _data[_type][::int(_timer.split('/')[0])]
        else:
            showerror(title='错误', message=msg)
            return []
    elif '-' in _timer and ',' not in _timer and '/' not in _timer:
        '''1-7'''
        _tmp = list(range(int(_timer.split('-')[0]),
                           int(_timer.split('-')[1]) + 1))
        _tmp = list(map(lambda x: int(x), _tmp))
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    elif ',' in _timer and '/' not in _timer and '-' not in _timer:
        '''1,2,3'''
        _tmp = list(map(lambda x: int(x), _timer.split(',')))
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    elif ',' not in _timer and '/' not in _timer and '-' not in _timer:
        '''1'''
        _tmp = [int(_timer)]
        if set(_tmp).issubset(set(_data[_type])):
            return _tmp
        else:
            showerror(title='错误', message=msg)
            return []
    else:
        showerror(title='错误', message='信息有错误[时间格式]或[命令为空]！')
        return []

def _Job():
    global IS_RUN
    ter = _t.get()
    if ter.split(' ').__len__() == 5:
        '''解析正确的格式的时间数据'''
        if ter.split(' ')[2] == '*' and ter.split(' ')[3] == '*':
            _min_list = _jiexi('min', ter.split(' ')[0])
            _hour_list = _jiexi('hour', ter.split(' ')[1])
            _day_list = _jiexi('day', ter.split(' ')[2])
            _mou_list = _jiexi('mou', ter.split(' ')[3])
            _week_list = _jiexi('week', ter.split(' ')[4])
            IS_RUN = True
            while 1:
                _now = datetime.now()
                _now_min = _now.minute
                _now_hour = _now.hour
                _now_day = _now.day
                _now_mou = _now.month
                _now_week = _now.weekday() + 1
                if _now_week in _week_list:
                    if _now_hour in _hour_list:
                        if _now_min in _min_list:
                            cmd = _c.get()
                            cur_path = _p.get()
                            if cur_path != '':
                                chdir(cur_path)
                            else:
                                chdir(path.abspath(path.curdir))
                            if '' != cmd:
                                lb.delete(0, END)
                                try:
                                    lb.insert(END, '...命令执行中...')
                                    try:
                                        pcmd = Popen(cmd, shell=True, stdout=PIPE,
                                                     stderr=PIPE)
                                        lb.delete(0, END)
                                        for i in iter(pcmd.stdout.readline, 'b'):
                                            if not i:
                                                break
                                            lb.insert(END, i.decode('gbk'))
                                    except Exception as e:
                                        print('路径有问题')
                                except Exception as e:
                                    lb.delete(0, END)
                                    lb.insert(END, e)
                            else:
                                showerror(title='错误', message='信息有错误[时间格式]或[命令为空]！')
                            sleep(1)
                            # 防止重复执行
                            if _now_min == _now.minute and _now_hour == _now.hour:
                                sleep(60 - _now.second)
                        else:
                            sleep(60)
                    else:
                        sleep(60 * 60)
                else:
                    sleep(24 * 60 * 60)
        else:
            showerror(title='错误', message='信息有错误[时间格式暂不支持日、月]！')
    else:
        showerror(title='错误', message='信息有错误[时间格式]或[命令为空]！')

def _check_title():
    while 1:
        if IS_RUN:
            root.title(_timer.timerRuningTitle + str(datetime.now())[:-7])
        else:
            root.title(_timer.timerTitle + str(datetime.now())[:-7])
        sleep(1)

def _choose_script_dir():
    global _p
    dir_name = filedialog.askdirectory()
    if '' != dir_name:
        _p.set(dir_name)

def _run():
    t1 = Thread(target=_Job,)
    t1.setDaemon(True)
    t1.start()

frame0 = Frame(master=root)
frame00 = Frame(master=frame0, width=75)
frame01 = Frame(master=frame0, width=75)
frame2 = Frame(master=root, width=75, height=50)
Label(master=frame00, text='定时表达式：').pack()
Entry(master=frame00, textvariable=_t, width=20).pack()
Button(master=frame01, text='脚本路径', command=_choose_script_dir).pack()
Entry(master=frame01, textvariable=_p, width=45).pack()
frame0.pack()
frame00.pack(side=LEFT, fill=Y)
frame01.pack(side=RIGHT, fill=Y)
Label(master=root, text='执行命令：').pack()
Entry(master=root, textvariable=_c, width=65).pack()
Button(master=root, text='开始运行', command=_run).pack()
lb = Listbox(frame2, width=65, height=50)
scr = Scrollbar(frame2)
lb.config(yscrollcommand=scr.set)
scr.config(command=lb.yview)
lb.pack(side=LEFT, fill=Y)
lb.insert(END, '...运行日志...')
scr.pack(side=RIGHT, fill=Y)
frame2.pack()

def main():
    t0 = Thread(target=_check_title, )
    t0.setDaemon(True)
    t0.start()
    root.mainloop()