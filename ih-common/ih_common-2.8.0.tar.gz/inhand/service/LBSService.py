import http.client
import json
import time
import ssl
import requests
from utilities.URLUtility import GenericURL
from utilities.DateTimeUtility import DatetimeUtility
from utilities.Utility import Utility
from utilities.GNSSTools import GNSSTools
import logging,traceback

class LBSService:
    def __init__(self,settings):
        import sys
        sys.path.append('../../')
        from utilities.URLUtility import GenericURL
        self.settings = settings
        self.url = GenericURL(settings.lbs.url)

        ssl._create_default_https_context = ssl._create_unverified_context

    def queryByAddress(self,address):
        logging.info('This is a parent class, there is nothing to do!')
        return None


    def query(self,longitude,latitude):
        logging.info('This is a parent class, there is nothing to do!')
        return None


    def queryLocationDesc(self,longitude,latitude):
        retry = 3
        address = None
        if self.validate(longitude,latitude):
            address = self.query(longitude,latitude)
            while address is None and retry > 0:
                address = self.query(longitude,latitude)
                retry = retry -1
                logging.warning("Retry to resolve the address[%f,%f] in %d times" % (latitude,longitude,retry))

        return address

    def validate(self,longitude,latitude):
        if longitude is None or latitude is None or (abs(longitude - 0.0) == 0.0001 and abs(latitude - 0.0) <= 0.0001):
            return False
        else:
            return True

    @staticmethod
    def createLBSService(settings):
        if settings.lbs.provider == 'baidu':
            return BaiduLBSService(settings)
        elif settings.lbs.provider == 'google':
            return GoogleLBSService(settings)
        elif settings.lbs.provider == 'gaode':
            return GaodeLBSService(settings)
        else:
            return None


class GoogleLBSService(LBSService):
    #https://developers.google.com/maps/documentation/geocoding/start
    #https://maps.googleapis.com/maps/api/geocode/json?latlng=40.714224,-73.96145&key=AIzaSyCjLe5tfpxlfNsdo9btD9PeMhRz3xmB5Jc
    def __init__(self,settings):
        LBSService.__init__(self,settings)

    def queryByAddress(self, address):
        logging.warning("To-Do: query address with google map api")
        return None

    def query(self,longitude,latitude):

        resource = ('%s?latlng=%f,%f&output=json&key=%s' % (self.url.path, latitude,longitude, self.url.params['key']))
        try:
            time.sleep(1)
            if self.url.scheme == 'http':
                conn = http.client.HTTPConnection(self.url.host)#httplib.HTTPConnection(host=self.url.host,timeout=30)
            else:
                conn = http.client.HTTPSConnection(self.url.host)#httplib.HTTPSConnection(host=self.url.host,timeout=30)p
            conn.request("GET", resource)
            r1 = conn.getresponse()
            if r1.status != 200:
                logging.warning("Location(%f,%f), result: %s, reason: %s, info: %s)" % (longitude, latitude, str(r1.status), r1.reason, r1.msg))
                return None
            else:
                result = json.loads(r1.read().decode("utf-8"))
                print(result)
                if 'results' in result.keys():
                    address = Address(longitude,latitude)
                    address_components=result['results'][0]['address_components']
                    address.address= result['results'][0]['formatted_address']

                    for c in address_components:
                        if 'administrative_area_level_1' in c['types']:
                            address.province = c['short_name']
                        elif 'administrative_area_level_2' in c['types']:
                            address.city = c['short_name']
                        elif 'country' in c['types']:
                            address.country=c['short_name']
                        elif 'locality' in c['types'] or 'administrative_area_level_3' in c['types']:
                            address.district=c['short_name']

                    return address
                else:
                    return None
        except Exception as e:
            logging.warning("While call %s%s, There is an exception: %s" % (self.url.host,resource,e))
            return None


class BaiduLBSService(LBSService):
    def __init__(self,settings):
        LBSService.__init__(self,settings)

    def query(self,longitude,latitude):
        ll = GNSSTools.gpstobd09(longitude,latitude)
        resource = ('%s?location=%f,%f&output=json&pois=1&ak=%s' % (self.url.path, ll[1], ll[0], self.url.params['ak']))
        conn = None
        result = ""

        r1=None
        try:
            time.sleep(1)
            if self.url.scheme == 'http':
                conn = http.client.HTTPConnection(self.url.host)#httplib.HTTPConnection(host=self.url.host,timeout=30)
            else:
                conn = http.client.HTTPSConnection(self.url.host)#httplib.HTTPSConnection(host=self.url.host,timeout=30)p
            conn.request("GET", resource)
            r1 = conn.getresponse()
            if r1.status != 200:
                logging.warning("Location(%f,%f), result: %s, reason: %s, info: %s)" % (longitude, latitude, str(r1.status), r1.reason, r1.msg))
                return None
            else:
                result = json.loads(r1.read().decode("utf-8"))
                if 'result' in result.keys():
                    # To-Do: 在计算出 [country,province/state,city,ditrict]的数据
                    address = Address(longitude,latitude)
                    address.address= result['result']['formatted_address']
                    address.country = result['result']['addressComponent']['country']
                    address.province = result['result']['addressComponent']['province']
                    address.city = result['result']['addressComponent']['city']
                    address.district = result['result']['addressComponent']['district']
                    address.town = result['result']['addressComponent']['town']
                    return address
                else:
                    return None
        except Exception as e:
            logging.warning("While call %s%s, There is an exception: %s" % (self.url.host,resource,e))
            return None

    def queryByAddress(self, address):
        try:
            payload={
                'ak': self.url.params['ak'],
                'output': 'json',
                'address': address
            }
            url='{}://{}{}'.format(self.url.scheme,self.url.host,self.url.path)
            r=requests.get(url,params=payload)
            ret = r.json()
            if ret['status']  == 0:
                lng = ret['result']['location']['lng']
                lat = ret['result']['location']['lat']
                location=self.query(lng,lat)
                return location
            else:
                location=Address(None,None)
                location.address=address
                return location
        except Exception as e:
            logging.exception(e)
            location=Address(None,None)
            location.address=address
            return location


class GaodeLBSService(LBSService):
    def __init__(self,settings):
        LBSService.__init__(self,settings)

    def queryByAddress(self, address):
        logging.warning("To-Do: query address with gaode map api")
        return None

    def query(self,longitude,latitude):
        resource = ('%s?location=%f,%f&output=json&roadlevel=1&key=%s' % (self.url.path, longitude, latitude, self.url.params['key']))
        conn = None
        result = ""

        r1=None
        try:
            time.sleep(1)
            if self.url.scheme == 'http':
                conn = http.client.HTTPConnection(self.url.host)#httplib.HTTPConnection(host=self.url.host,timeout=30)
            else:
                conn = http.client.HTTPSConnection(self.url.host)#httplib.HTTPSConnection(host=self.url.host,timeout=30)p
            conn.request("GET", resource)
            r1 = conn.getresponse()
            if r1.status != 200:
                logging.warning("Location(%f,%f), result: %s, reason: %s, info: %s)" % (longitude, latitude, str(r1.status), r1.reason, r1.msg))
                return None
            else:
                result = json.loads(r1.read().decode("utf-8"))
                if 'regeocode' in result.keys():
                    # To-Do: 在计算出 [country,province/state,city,ditrict]的数据
                    address = Address(longitude,latitude)
                    address.address= result['regeocode']['formatted_address']
                    address.country = result['regeocode']['addressComponent']['country']
                    address.province = result['regeocode']['addressComponent']['province']
                    address.city = result['regeocode']['addressComponent']['city']
                    address.district = result['regeocode']['addressComponent']['district']
                    address.town = result['regeocode']['addressComponent']['township']
                    return address
                else:
                    return None
        except Exception as e:
            logging.warning("While call %s%s, There is an exception: %s" % (self.url.host,resource,e))
            return None





class Address:
    def __init__(self,longitude,latitude):
        self.country=''
        self.province=''
        self.city=''
        self.district=''
        self.town=''
        self.address=''
        if longitude is not None and latitude is not None:
            self.lnglat={'x':longitude,'y':latitude}
        else:
            self.lnglat=None

    def toMap(self):
        return {'address':self.address,'country':self.country,'province':self.province,'city':self.city,'town':self.town,'district':self.district,'lnglat':self.lnglat}


if __name__ == '__main__':
    import sys

    sys.path.append('../../')
    from Settings import Settings
    settings=Settings.readLocalSettings(path="../../../../test.json")

    #lsbsvc = GaodeLBSService(settings)
    #r = lsbsvc.queryLocationDesc(116.314049758,40.069384452)
    #r = lsbsvc.queryLocationDesc(116.481488,39.990464)
    #print('%s' % (r.toMap()))
    #print('%s' % (json.dumps(r)))
    lbssvc=BaiduLBSService(settings)
    r=lbssvc.queryByAddress("云南省昭通市水富县人民西路36号")
    print('%s' % (r.toMap()))