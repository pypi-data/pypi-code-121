
import sys
import time
import socket
import OpenSSL
import pandas as pd

if sys.version_info[0] < 3:
    import urllib2 as urlreq
    import httplib as httpclient
else:
    import urllib.request as urlreq
    import http.client as httpclient
# Works with suds with python 2.7, suds-jurko with python 3.6
from suds.client import Client
from suds.transport.http import HttpTransport, Reply, TransportError

class HTTPSClientAuthHandler(urlreq.HTTPSHandler):
    def __init__(self, key, cert):
        urlreq.HTTPSHandler.__init__(self)
        self.key = key
        self.cert = cert

    def https_open(self, req):
        # Rather than pass in a reference to a connection class, we pass in
        # a reference to a function which, for all intents and purposes,
        # will behave as a constructor
        return self.do_open(self.getConnection, req)

    def getConnection(self, host, timeout=300):
        return httpclient.HTTPSConnection(host,
                                          key_file=self.key,
                                          cert_file=self.cert)


class HTTPSClientCertTransport(HttpTransport):
    def __init__(self, key, cert, *args, **kwargs):
        HttpTransport.__init__(self, *args, **kwargs)
        self.key = key
        self.cert = cert

    def u2open(self, u2request):
        """
        Open a connection.
        @param u2request: A urllib2/url.request request.
        @type u2request: urllib2.Requet//url.request.
        @return: The opened file-like urllib2 object.
        @rtype: fp
        """
        tm = self.options.timeout
        url = urlreq.build_opener(HTTPSClientAuthHandler(self.key, self.cert))
        if self.u2ver() < 2.6:
            socket.setdefaulttimeout(tm)
            return url.open(u2request)
        else:
            return url.open(u2request, timeout=tm)


def prepare_key():
    password = ""
    p12 = OpenSSL.crypto.load_pkcs12(open("dl792115.p12", 'rb').read(), password)

    certFile = open("cert.pem", "wb")
    keyFile = open("key.pem", "wb")

    certFile.write(OpenSSL.crypto.dump_certificate(OpenSSL.crypto.FILETYPE_PEM, p12.get_certificate()))
    keyFile.write(OpenSSL.crypto.dump_privatekey(OpenSSL.crypto.FILETYPE_PEM, p12.get_privatekey()))

    certFile.close()
    keyFile.close()

class NapoleonDLWSConnector:
    def __init__(self, key_path, cert_path):
        self.key_path = key_path
        self.cert_path = cert_path
        self.wsdl_uri = 'https://service.bloomberg.com/assets/dl/dlws.wsdl'


    def request_ticker(self, tickers, requested_field, max_retry = 5, seconds_sleeping_delay = 30):
        c = Client(self.wsdl_uri, transport=HTTPSClientCertTransport(self.key_path,self.cert_path))
        submitGetDataReq = c.factory.create('SubmitGetDataRequest')
        # define the header section of the request
        reqHeaders = c.factory.create('GetDataHeaders')

        reqHeaders.dateformat = None
        reqHeaders.diffflag = None
        reqHeaders.secid = None
        reqHeaders.specialchar = None
        reqHeaders.version = None
        reqHeaders.yellowkey = None
        reqHeaders.bvaltier = None
        reqHeaders.bvalsnapshot = None
        reqHeaders.portsecdes = None
        reqHeaders.secmaster = True

        reqHeaders.closingvalues = True
        reqHeaders.derived = None
        progFlag = c.factory.create('ProgramFlag')
        # reqHeaders.programflag = None  # progFlag.oneshot
        reqHeaders.programflag = progFlag.adhoc
        regSolvency = c.factory.create('RegSolvency')
        reqHeaders.regsolvency = None  # regSolvency.no

        submitGetDataReq.headers = reqHeaders
        # define the list of fields that you wish to have for all the tickers
        reqFields = c.factory.create('Fields')
        reqFields.field.append('TICKER')
        reqFields.field.append(requested_field)
        #    reqFields.field.append('PX_BID')
        #    reqFields.field.append('PX_ASK')

        submitGetDataReq.fields = reqFields

        bvalFieldSets = c.factory.create("BvalFieldSets")

        # define the tickers you wish to get data for
        reqInstruments = c.factory.create('Instruments')

        for tick_label in tickers:
            ticker = c.factory.create('Instrument')
            ticker.id = tick_label
            marketSector = c.factory.create('MarketSector')
            # ticker.yellowkey = marketSector.Index
            instrumentType = c.factory.create('InstrumentType')
            # ticker.type = instrumentType.TICKER
            reqInstruments.instrument.append(ticker)


        # ticker2 = c.factory.create('Instrument')
        # ticker2.id = 'SCOZ7'
        # marketSector = c.factory.create('MarketSector')
        # ticker2.yellowkey = marketSector.Comdty
        # instrumentType = c.factory.create('InstrumentType')
        # ticker2.type = None  # instrumentType.TICKER
        # reqInstruments.instrument.append(ticker2)
        #
        # ticker = c.factory.create('Instrument')
        # ticker.id = 'IOEK8 ELEC'
        # marketSector = c.factory.create('MarketSector')
        # ticker.yellowkey = marketSector.Comdty
        # ticker.type = None
        # reqInstruments.instrument.append(ticker)
        #
        # ticker = c.factory.create('Instrument')
        # ticker.id = 'IOEK8 PIT'
        # marketSector = c.factory.create('MarketSector')
        # ticker.yellowkey = marketSector.Comdty
        # ticker.type = None
        # reqInstruments.instrument.append(ticker)

        submitGetDataReq.instruments = reqInstruments
        print('submitting request')
        print(submitGetDataReq)
        # send the request to request to Bloomberg Web Services interface.
        req = c.service.submitGetDataRequest(reqHeaders, bvalFieldSets, reqFields, reqInstruments)

        if req.statusCode.code != 0 or req.statusCode.description != "Success":
            # raise Exception.
            return ()

        print("Request Done!")
        print(req.statusCode.code)
        print(req.statusCode.description)
        print(req.responseId)
        print(req.requestId)

        resp = c.service.retrieveGetDataResponse(req.responseId)
        counter = 0
        while resp.statusCode.code != 0 and counter < max_retry:
            time.sleep(seconds_sleeping_delay)
            print('retrying ' + str(counter))
            resp = c.service.retrieveGetDataResponse(req.responseId)
            counter = counter + 1
        if resp.statusCode.code != 0:
            raise Exception('request not found')
        requested_values = []
        for inst_data in resp.instrumentDatas.instrumentData:
            instrument_value = {}
            instrument_ticker = str(inst_data.instrument.id + ' ' + inst_data.instrument.yellowkey)
            instrument_value['ticker'] = instrument_ticker
            print('request answer for instrument ' + str(inst_data.instrument))
            print(instrument_ticker)
            if len(inst_data.data) < 2:
                raise Exception('no request value')
            instrument_value[requested_field] = str(inst_data.data[1]._value)
            requested_values.append(instrument_value)
        values_df = pd.DataFrame(requested_values)
        return values_df

