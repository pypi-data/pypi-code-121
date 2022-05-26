from socket import *
import threading
import json
import os

address='10.219.33.45'
port=2159
buffsize=1024
s = socket(AF_INET, SOCK_STREAM)
s.bind((address,port))
s.listen(100)     #max connect
conn_list = []
conn_dt = {}
requeststack = {}

def tcplink(sock,addr):
    while True:
        try:
            recvdata=sock.recv(buffsize).decode('utf-8')
            curdic = json.loads(recvdata)
            if curdic['module'] == 'clientA' and curdic['method'] == 'requestA':
                requeststack[curdic['token']] = [0,'',[curdic['srcFile'],curdic['testFile'],curdic['samplerate']]]
                while True:
                    if requeststack[curdic['token']][1] != '':
                        oneresult = requeststack.pop(curdic['token'])[1]
                        curdic['result'] = oneresult
                        sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                        os.system("rm -rf /home/netease/polqa/" + curdic['token'])
                        break

            if curdic['module'] == 'clientB' and curdic['method'] == 'requestB':
                if len(requeststack) != 0:
                    for onekey in requeststack:
                        if requeststack[onekey][0] == 0:
                            requeststack[onekey][0] = 1
                            curdic['token'] =  onekey
                            curdic['job'] = 'occupy'
                            curdic['srcFile'] = requeststack[onekey][2][0]
                            curdic['testFile'] = requeststack[onekey][2][1]
                            curdic['samplerate'] = requeststack[onekey][2][2]
                            sock.send(bytes(json.dumps(curdic), encoding='utf-8'))
                            break
                    else:
                        curdic['job'] = None
                        sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
                else:
                    curdic['job'] = None
                    sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
            if curdic['module'] == 'clientB' and curdic['method'] == 'response':
                requeststack[curdic['token']][1] = curdic['result']
                sock.send(bytes(json.dumps(curdic),encoding='utf-8'))
            if not recvdata:
                break
        except:
            sock.close()
            print(addr,'offline')
            _index = conn_list.index(addr)
            conn_dt.pop(addr)
            conn_list.pop(_index)
            break

def recs():
    while True:
        clientsock,clientaddress=s.accept()
        if clientaddress not in conn_list:
            conn_list.append(clientaddress)
            conn_dt[clientaddress] = clientsock
        print('connect from:',clientaddress)
        #
        t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))
        t.start()

if __name__ == '__main__':
    t1 = threading.Thread(target=recs, args=(), name='rec')

    t1.start()

