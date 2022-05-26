#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import sys
import logging
import asyncio
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asyncrequest import async_soap_request
from lycium.asynchttphandler import async_route
from lycium.webapplication import WebApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger('zeep.wsdl.wsdl').setLevel(logging.DEBUG)
logging.getLogger('zeep.xsd.schema').setLevel(logging.DEBUG)
logging.getLogger('zeep.transports').setLevel(logging.DEBUG)

LOG = logging.getLogger('async.request')

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_wsdl(handler, request):
    host = '127.0.0.1'
    result, err = yield async_soap_request('http://%s/wsdl/yytwebservice/n_webservice.asmx?WSDL' % (host),
        'uf_getsult',
        '<request><requestHead><busCode>1019</busCode><operNo>1FMZ001</operNo><terminalNo>1FMZ001</terminalNo><tradeDate>20210526</tradeDate><tradeTime>090311</tradeTime></requestHead><data><hosCardNo>64032419940810328X</hosCardNo><hosCardType>5</hosCardType><dateStart>20210524</dateStart><dateEnd>20210526</dateEnd><requestPage /><pageSize /><prescriptionFrom>1</prescriptionFrom><tranFlow /></data></request>'
    )
    print(result, err)
    return str(result)

def main():
    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
