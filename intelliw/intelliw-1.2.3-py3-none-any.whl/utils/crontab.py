'''
Author: Hexu
Date: 2022-05-05 12:07:16
LastEditors: Hexu
LastEditTime: 2022-05-05 14:46:02
FilePath: /iw-algo-fx/intelliw/utils/crontab.py
Description: crontab
'''
import time
import datetime
import threading
import types

class CrontabError(Exception):
    pass

class Crontab:
    """Crontab 定时任务模块
        Args:
            job (dict): name crontab func args
            max_thread_limit (int, optional): 最大线程执行数 Defaults to max_thread_limit?max_thread_limit:len(job).
            logger (_type_, optional): 日志 Defaults to None.
    """ 
    def __init__(self, job, logger=None):
        self.job = job
        self.logger = logger
        self.thread_list = []
        self.max_thread_limit = len(job)

    def check(self):
        def exit_display():
            exit("joblist like [ {'name':str,'crontab':str,'func':FunctionType,'args':tuple}, ... ]")

        k = ['name', 'func', 'args', 'crontab']
        for one in self.job:
            for i in k:
                if i not in one.keys():
                    exit_display()
            if type(one['name']) is not str:
                exit_display()
            if type(one['crontab']) is not str:
                exit_display()
            if not isinstance(one['func'], types.FunctionType):
                exit_display()
            if type(one['args']) is not tuple:
                exit_display()
        return 0

    def min_clock(self, s):
        while True:
            tim = datetime.datetime.now().strftime('%H:%M:%S').split(":")
            if tim[2] == s:
                time.sleep(1)
                return 0
            else:
                time.sleep(0.5)

    @staticmethod
    def x_crontab(string: str, xtype: str):
        def x_list(i: int, xtype: str):
            if xtype == 'min':
                return [str(x) for x in range(0, 60, i)]
            elif xtype == 'hour':
                return [str(x) for x in range(0, 24, i)]
            elif xtype == 'day':
                return [str(x) for x in range(1, 32, i)]
            elif xtype == 'month':
                return [str(x) for x in range(1, 13, i)]
            else:
                return [str(i)]

        for x in string:
            if x not in "*/,0123456789":
                raise CrontabError('crontab config error')
        if string == '*':
            return [None]
        elif string.startswith('*/'):
            try:
                return x_list(int(string[2:]), xtype=xtype)
            except Exception as e:
                raise CrontabError('crontab config error')
        elif ',' in string:
            return string.split(',')
        elif string.isdigit:
            return [string]
        else:
            raise CrontabError('crontab config error')

    def init_job(self, crontab_list):
        if len(crontab_list) != 5:
            raise CrontabError('crontab config error')
        CTM = [self.x_crontab(crontab_list[0], xtype='min'), self.x_crontab(crontab_list[1], xtype='hour'), self.x_crontab(crontab_list[2], xtype='day'),
               self.x_crontab(crontab_list[3], xtype='month'), self.x_crontab(crontab_list[4], xtype='weekday'), ]
        for i in CTM:
            if type(i) is not list:
                raise CrontabError('crontab config error')
        return CTM

    def x_job(self):
        x_job = []
        for one in self.job:
            _job = {}
            ctb = self.init_job([x for x in one['crontab'].split(' ') if x != ''])

            _job.setdefault('name', one['name'] if type(one['name']) is str else None)
            _job.setdefault('crontab', ctb if type(ctb) is list else None)
            _job.setdefault('func', one['func'] if isinstance(one['func'], types.FunctionType) else None)
            _job.setdefault('args', one['args'] if type(one['args']) is tuple else None)
            x_job.append(_job)
        return x_job

    def create_subthread(self, func, args, daemon=True, is_wait_end=False):
        try:
            st = threading.Thread(target=func, args=tuple(args), )
            if daemon == True:
                st.daemon = True
            st.start()
            if is_wait_end == True:
                st.join()
            return [st]
        except Exception as e:
            return 'error', str(e)

    # assert one['name'] is str,  one['crontab'] len 5  , one['func'] is func ,one['args'] is tuple
    def run(self):
        if self.check() == 0:
            while True:
                for st in self.thread_list:
                    if not st.isAlive():
                        self.thread_list.remove(st)

                if len(self.thread_list) > self.max_thread_limit:
                    if self.logger:
                        self.logger.info('max_thread_limit overflow '+str(str(datetime.datetime.now()))+'\n\n')
                    return -1

                self.min_clock('00')
                TM = [str(tm) for tm in time.localtime()]
                TM = [TM[4], TM[3], TM[2], TM[1], TM[6]]

                log = ''
                for one in self.x_job():
                    if type(one['crontab']) is not list:
                        log += str(one['crontab']) + ': ' + str(one['name']) + '\n\n'
                        continue

                    for i in range(len(one['crontab'])):
                        if one['crontab'][i] == [None] or TM[i] in one['crontab'][i]:
                            pass
                        else:
                            break
                    else:
                        res = self.create_subthread(one['func'], args=one['args'], daemon=True, is_wait_end=False)
                        if len(res) == 2:
                            log += 'crontab job run error: ' + str(one['name']) + '\n\n'
                        else:
                            self.thread_list.append(res[0])
                if self.logger and log != '':
                    self.logger.info('===================='+str(datetime.datetime.now())+'====================\n'+log)
                    self.logger.info('===================='+str(datetime.datetime.now())+'====================\n\n')


if __name__ == '__main__':
    def p(*args):
        print(args,datetime.datetime.now())
        print('====\n')

    joblist = [
        {'name':'job1','crontab':'*/1 * * * 0,1,2,3,4,5,6','func':p ,'args':('job1',)},
        {'name': 'job2', 'crontab': '*/2 * * * 0,1,2,3,4,5,6', 'func': p, 'args': ('job2',)},
        {'name': 'job3', 'crontab': '*/3 * * * 0,1,2,3,4,5,6', 'func': p, 'args': ('job3',)},
    ]

    crontab1 = Crontab(joblist)
    crontab1.run()


