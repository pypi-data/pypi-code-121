# /*
#  * @Author: Guofeng He 
#  * @Date: 2022-05-14 08:59:31 
#  * @Last Modified by:   Guofeng He 
#  * @Last Modified time: 2022-05-14 08:59:31 
#  */

# coding=utf-8

'''
提供基本的通信封装
'''

import logging
import socket
import traceback
from _thread import start_new_thread
import ping3

from select import select

class NetTools(object):
    def __init__(self) -> None:
        pass

    def latency(dst_ip):
        ''' 测试到目标地址的时延
        '''
        return ping3.ping(dst_ip)
        

class Session(object):
    def __init__(self,sock,local_id,peer_id=None,dst=None,receive_handle=None) -> None:
        self.peer_id = peer_id
        self.local_id = local_id
        self.sock,self.dst,self.receive_handle = sock,dst,receive_handle
        pass


    def send(self,data):
        if self.dst:
            logging.debug("send to %s:%d\n    (%d) %s ..." % (self.dst[0], self.dst[1],len(data), ''.join('{:02x} '.format(x) for x in data[:16])))
            return self.sock.sendto(data,self.dst)
        else:
            raise("No dst")
    
    def received_process(self,data,src,sock):
        if self.receive_handle:
            self.receive_handle(data,src,self)
        else:
            logging.warning("No handle for this session!")
        pass

    def close(self):
        self.sock.close()


    

class CommEngine(object):
    # class PPCommEngineBlock(object):  #udp
    '''
    pce = PPCommEngine(timeout=5,mode="autoclose")

    sock = pce.initsock(("0.0.0.0",5555))
    pce.wait_receive(sock,post_receive)
    ...
    pce.send(sock,data,dst)
    ...
    pce.close(sock)

    pce.quit()


    '''

    def __init__(self, config={}):
        '''

        :param timeout:
        :param com_type:
        :param mode: autoclose will auto close the socket when connectreset event,
                      notclose will remain socket when connectreset event,
        '''
        self.timeout, self.com_type = config.get("timeout",5), config.get("com_type","udp")
        self.mode = config.get("mode","notclose")
        self.quitting = False
        self.sessions = []

    def start_session(self,local_id,peer_id=None,bind_addr=None,dst_addr=None,receive_handle=None):
        sock = self.initsock(bind_addr)
        session = Session(sock,local_id,peer_id,dst_addr,receive_handle)
        if receive_handle:
            self.wait_receive(sock,session.received_process)
        self.sessions.append(session)
        return session

    def end_session(self,session):
        session.close()
        self.sessions.remove(session)

    def senddata(self,session,data):
        if session.dst:
            self.send_now(session.sock,data,session.dst)
        else:
            raise("No dst")

    def initsock(self, bind_addr=None):
        if self.com_type == "udp":
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(self.timeout)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # s.setblocking(False)
        else:  # tcp
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(self.timeout)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setblocking(False)
        if bind_addr:
            logging.debug("bind to {}:{}".format(bind_addr[0],bind_addr[1]))
            s.bind(bind_addr)
        return s


    def bind(self, sock, bind_addr=("0.0.0.0", 0)):
        if bind_addr[1]:
            sock.bind(bind_addr)
            return True
        return False

    def close(self, sock):
        try:
            sock.close()
        except Exception as e:
            logging.warning(repr(e))
            pass

    def connect(self, sock, dst):
        pass

    def wait_accept(self, sock, post_accept):
        '''
        post_accept is callback,post_accept(srcaddr)
        after accept will new thread to call post_accept
        '''
        pass

    def wait_accept_receive(self, sock, post_accept, post_receive):
        '''
        post_accept is callback,post_accept(srcaddr)
        after accept will new thread to call post_accept
        '''
        self.wait_receive(sock, post_receive)
        pass

    def receive(self, sock, num):
        '''
        :param sock:
        :param num:
        :return: data,addr
        '''
        return sock.recvfrom(num)

    def send_now(self, sock, data, dst):
        logging.debug("send to %s:%d\n %s" % (dst[0], dst[1], ''.join('{:02x} '.format(x) for x in data[:16])))
        return sock.sendto(data, dst)

    def send(self, sock, data, dst):
        # if isinstance(sock, PPSocket):
        #     return sock.send(data, dst)
        # else:
        return self.send_now(sock, data, dst)

    def get_sock_id(self, sock):
        return tuple([sock.fileno()])

    def wait_receive(self, sock, post_receive):
        '''
        :param post_receive is callback, if sock have data will call post_receive
        :param post_receive(data,srcaddr,sock)
            data  receive data  if =="" conect is closed
            srcaddr  is data from
            sock is sock self, if sock closed,will return None
        :return None

        '''
        # if isinstance(sock, PPNetNode):
        #     sock.wait_receive(post_receive)
        # else:
        start_new_thread(self.do_receive, (sock, post_receive))
        pass

    def do_receive(self, sock, post_receive):
        while not self.quitting:
            try:
                if sock.fileno() == -1:
                    break
                data, addr = sock.recvfrom(1522)
                logging.debug(
                    "receive from %s:%d\n    (%d) %s" % (addr[0], addr[1],len(data), ''.join('{:02x} '.format(x) for x in data[:20])))
                try:
                    post_receive(data, addr, sock)
                except Exception as e:
                    logging.debug(traceback.format_exc())
                    logging.warning(repr(e))
            except socket.timeout:
                continue
            except OSError:
                break
            except ConnectionResetError as exp:
                logging.warning(repr(exp))
                post_receive(b"", None, None)
                break
            except Exception as exp:
                logging.debug(traceback.format_exc())

    def quit(self):
        self.quitting = True


class CommEngineTCP(object):
    def __init__(self,timeout=5):
        self.timeout = timeout
        self.status = {}
        self.quitting=False

    def initsock(self,bind_addr=None,timeout=0):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not timeout:
            timeout = self.timeout
        s.settimeout(timeout)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if bind_addr:
            s.bind(bind_addr)
        return s

    def connect(self,sock,dst):
        try:
            sock.connect(dst)
        except socket.error as exp:
            logging.warning("connect error %s"%(repr(exp)))

    def wait_accept_receive(self,sock,post_accept,post_receive):
        '''
        post_accept is callback,post_accept(srcaddr),if return false will quit refuse connect
        after accept will new thread to call post_accept
        '''
        sock.listen(10)
        while not self.quitting:
            try:
                conn,addr = sock.accept()
                logging.debug("accept from %s %d:\n"%(addr[0],addr[1]))  
                if post_accept(conn,addr):
                    start_new_thread(self.connection_receive,(conn,addr,post_receive))
            except socket.timeout:
                continue
            except OSError as exp:
                logging.warning(repr(exp))
                break
            except Exception as exp:
                logging.warning(repr(exp))        
    
    def wait_accept(self,sock,post_accept):
        '''
        post_accept is callback,post_accept(srcaddr)
        after accept will new thread to call post_accept
        '''
        sock.listen(10)
        logging.debug("start listening on %s %d"%sock.getsockname())
        while not self.quitting:
            try:
                addr = ("0.0.0.0",0)
                conn,addr = sock.accept()
                logging.debug("accept from %s %d:\n"%(addr[0],addr[1]))  
                post_accept(conn,addr)
            except socket.timeout:
                continue
            except ConnectionResetError:
                logging.debug("connect reset by peer.%s %d"%(addr[0],addr[1]))
                break
            except OSError as exp:
                logging.warning(repr(exp))
                break
            except Exception as exp:
                logging.warning(repr(exp))         

    def _post_accept(self,conn,addr,post_receive):
        start_new_thread(self.connection_receive,(conn,addr,post_receive))
        return True

    def receive(self,sock,num):
        return sock.recv(num),sock.getpeername()

    def send(self,sock,data,dst):
        logging.debug("send to %s %d:\n%s"%(dst[0],dst[1],''.join('{:02x} '.format(x) for x in data)))  
        return sock.send(data)  

    def wait_receive(self,sock,post_receive):
        '''
        post_receive is callback,post_accept(data,srcaddr)
        will call post_receive
        '''
        self.wait_accept_receive(sock,self._post_accept,post_receive)

    def connection_receive(self,sock,addr,post_receive):
        '''

        :param sock:
        :param addr:
        :param post_receive: return ture continue receive,false will quit receive
        :return:
        '''
        while not self.quitting:
            try:
                data = sock.recv(1522)
                logging.debug("receive from %s:%d\n %s"%(addr[0],addr[1],''.join('{:02x} '.format(x) for x in data)))
                if not len(data):
                    break
                if post_receive(data,addr,sock):
                    continue
                else:
                    break
            except socket.timeout:
                logging.debug("sock timeout %s %d"%addr)
                sock.close()
                break
            except ConnectionResetError:
                logging.debug("connect reset by peer.%s %d"%addr)
                post_receive(b"",addr,sock)
                break
            except Exception as exp:
                print(traceback.format_exc())
                logging.warning(repr(exp))
                break
        pass    
    def quit(self):
        self.quitting = True


