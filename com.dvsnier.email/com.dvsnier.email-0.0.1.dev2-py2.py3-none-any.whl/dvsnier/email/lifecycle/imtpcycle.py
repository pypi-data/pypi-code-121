# -*- coding:utf-8 -*-

from com.dvsnier.email.lifecycle.icycle import ICycle


class IMTPCycle(ICycle, object):
    ''' the cycle interface class '''
    def __init__(self):
        super(IMTPCycle, self).__init__()

    def connect(self, host, port):
        ''' the connect remote server that a host on a given port. The defaults are to connect to the local host at the standard SMTP port (25). '''
        pass

    def login(self, user, password):
        ''' the login in remote server that requires authentication.  '''
        pass

    def sendmail(self, from_addr, to_addrs, msg):
        '''
            Send mail. The required arguments are an RFC 822 from-address string, a list of RFC 822 to-address strings (a bare string will  be treated as a list with 1 address), and a message string.
        '''
        pass

    def quit(self):
        ''' the Terminate the SMTP session and close the connection.
            Return the result of the SMTP QUIT command. '''
        pass
