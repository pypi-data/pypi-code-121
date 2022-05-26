# -*- coding:utf-8 -*-
import sys
import  os,time
from os import path
import copy
sys.path.append(os.path.dirname(path.dirname(__file__)))
from commFunction import global_result,sftp_connect,sftp_get,sftp_disconnect,constMosResult
import shutil
from  socketClient import SocketClient
from POLQA import startvqt


def exec_polqa_test():

    while(True):
        try:
            socket = SocketClient(global_result.machost,global_result.PORT)
            curdata = global_result.get_data()
            curdata['module'] = 'clientB'
            curdata['method'] = 'requestB'
            curruslt = socket.sender(curdata)
        except:
            socket.close()
            continue
        if curruslt['job'] is None or str(curruslt['job']) == 'null':
            continue

        #try:
        print('processing')
        #检查文件

        #链接sftp
        client,sftp = sftp_connect(global_result.username,global_result.password,global_result.HOST,port=global_result.sftpPort)
        sftp_get(sftp, '/home/netease/polqa/' + curruslt['token'], '')
        sftp_disconnect(client)
        srf ,tsf, fpath,sr = curruslt['token'] +'/'+ curruslt['srcFile'],curruslt['token'] +'/'+ curruslt['testFile'],curruslt['token'],curruslt['samplerate']
        if not os.path.exists(srf) or not os.path.exists(tsf):
            curruslt['result'] = 'lack of input files!'
            socket = SocketClient(global_result.machost, global_result.PORT)
            curruslt['module'] = 'clientB'
            curruslt['method'] = 'response'
            try:
                douresult = socket.sender(curruslt)
            except:
                socket.close()
                shutil.rmtree(fpath)
                print(fpath,' is not exist')
            continue

        # samplerate = info[3]
        global_result.mosResult = copy.deepcopy(constMosResult)
        startvqt(os.path.abspath(srf), os.path.abspath(tsf), sr)
        curruslt['result'] = global_result.mosResult

        socket = SocketClient(global_result.machost, global_result.PORT)
        curruslt['module'] = 'clientB'
        curruslt['method'] = 'response'
        print(curruslt)
        try:
            socket.sender(curruslt)
        except:
            socket.close()
            time.sleep(1)
            shutil.rmtree(fpath)
            print('file was not deleted!')



if __name__ == '__main__':
    exec_polqa_test()  #0 从头开始  #-1 从尾开始