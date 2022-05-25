import json
import math
import sys


class GNSSTools:
    x_pi = 3.14159265358979324 * 3000.0 / 180.0
    pi = 3.1415926535897932384626
    a = 6378245.0
    ee = 0.00669342162296594323

    @staticmethod
    def gpstobd09(lng, lat):
        [gcj_lng,gcj_lat] = GNSSTools.wgs84togcj02(lng,lat)
        [bd_lng,bd_lat] = GNSSTools.gcj02tobd09(gcj_lng,gcj_lat)
        return [bd_lng, bd_lat]


    @staticmethod
    def gcj02tobd09(lng, lat):
        z = math.sqrt(lng * lng + lat * lat) + 0.00002 * math.sin(lat * GNSSTools.x_pi)
        theta = math.atan2(lat, lng) + 0.000003 * math.cos(lng * GNSSTools.x_pi)
        bd_lng = z * math.cos(theta) + 0.0065
        bd_lat = z * math.sin(theta) + 0.006
        return [bd_lng, bd_lat]

    @staticmethod
    def bd09togcj02(bd_lon, bd_lat):
        x = bd_lon - 0.0065
        y = bd_lat - 0.006
        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * GNSSTools.x_pi)
        theta = math.atan2(y, x) - 0.000003 * math.cos(x * GNSSTools.x_pi)
        gg_lng = z * math.cos(theta)
        gg_lat = z * math.sin(theta)
        return [gg_lng, gg_lat]

    @staticmethod
    def wgs84togcj02(lng, lat):
        if GNSSTools.out_of_china(lng, lat):
            return lng, lat
        dlat = GNSSTools.transformlat(lng - 105.0, lat - 35.0)
        dlng = GNSSTools.transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * GNSSTools.pi
        magic = math.sin(radlat)
        magic = 1 - GNSSTools.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((GNSSTools.a * (1 - GNSSTools.ee)) / (magic * sqrtmagic) * GNSSTools.pi)
        dlng = (dlng * 180.0) / (GNSSTools.a / sqrtmagic * math.cos(radlat) * GNSSTools.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [mglng, mglat]

    @staticmethod
    def gcj02towgs84(lng, lat):
        if GNSSTools.out_of_china(lng, lat):
            return lng, lat
        dlat = GNSSTools.transformlat(lng - 105.0, lat - 35.0)
        dlng = GNSSTools.transformlng(lng - 105.0, lat - 35.0)
        radlat = lat / 180.0 * GNSSTools.pi
        magic = math.sin(radlat)
        magic = 1 - GNSSTools.ee * magic * magic
        sqrtmagic = math.sqrt(magic)
        dlat = (dlat * 180.0) / ((GNSSTools.a * (1 - GNSSTools.ee)) / (magic * sqrtmagic) * GNSSTools.pi)
        dlng = (dlng * 180.0) / (GNSSTools.a / sqrtmagic * math.cos(radlat) * GNSSTools.pi)
        mglat = lat + dlat
        mglng = lng + dlng
        return [lng * 2 - mglng, lat * 2 - mglat]

    @staticmethod
    def transformlat(lng, lat):
        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
                0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * GNSSTools.pi) + 20.0 *
                math.sin(2.0 * lng * GNSSTools.pi)) *2.0 / 3.0
        ret += (20.0 * math.sin(lat * GNSSTools.pi) + 40.0 *
                math.sin(lat / 3.0 * GNSSTools.pi)) *2.0 / 3.0
        ret += (160.0 * math.sin(lat / 12.0 *GNSSTools. pi) + 320 *
                math.sin(lat * GNSSTools.pi / 30.0)) *2.0 / 3.0
        return ret

    @staticmethod
    def transformlng(lng, lat):
        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
                0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))

        ret += (20.0 * math.sin(6.0 * lng * GNSSTools.pi) + 20.0 *
                math.sin(2.0 * lng * GNSSTools.pi)) *2.0 / 3.0
        ret += (20.0 * math.sin(lng *GNSSTools.pi) + 40.0 *
                math.sin(lng / 3.0 * GNSSTools.pi)) *2.0 / 3.0
        ret += (150.0 * math.sin(lng / 12.0 * GNSSTools.pi) + 300.0 *
                math.sin(lng / 30.0 * GNSSTools.pi)) *2.0 / 3.0
        return ret

    @staticmethod
    def out_of_china(lng, lat):
        if lng < 72.004 or lng > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False

    @staticmethod
    def processJson(inputJsonFile, outputJsonFile):
        file_grid = outputJsonFile + "_grid.json"

        file_heat = outputJsonFile + "_heat.json"
        fin = open(inputJsonFile, 'r')
        fout = open(file_heat, 'w')
        fout_ = open(file_grid, 'w')

        out = []
        out_ = []
        for eachLine in fin:
            fileName, leftLon, rightLon, topLat, bottomLat, cnt, color = eachLine.split(",")
        data = {}
        data_ = {}
        result1 = GNSSTools.wgs84togcj02(float(leftLon), float(topLat))
        result2 = GNSSTools.gcj02tobd09(result1[0], result1[1])
        result3 = GNSSTools.wgs84togcj02(float(rightLon), float(bottomLat))
        result4 = GNSSTools.gcj02tobd09(result3[0], result3[1])
        data["lat"] = result2[1]
        data["lng"] = result2[0]
        data["count"] = cnt
        out += [data]


        data_["topLat"] = result2[1]
        data_["leftLon"] = result2[0]
        data_["bottomLat"] = result4[1]
        data_["rightLon"] = result4[0]
        data_["cnt"] = cnt
        data_["color"] = color
        out_ += [data_]


        fout.write(str(out))
        fout_.write(str(out_))
        fin.close()
        fout.close()
        fout_.close()

    @staticmethod
    def processCSV(inputJsonFile, outputJsonFile):
        file_csv = outputJsonFile + ".csv"

        fin = open(inputJsonFile, 'r')
        fout = open(file_csv, 'w')

        for eachLine in fin:
            fileName, addr, topLat, leftLon = eachLine.split(",")
        result1 = GNSSTools.bd09togcj02(float(leftLon), float(topLat))
        result2 = GNSSTools.gcj02towgs84(result1[0], result1[1])
        out = str(fileName) + "," + str(addr) + "," + str(result2[0]) + "," + str(result2[1]) + "\n"
        fout.write(str(out))
        fin.close()
        fout.close()

if __name__ == '__main__':
    ll=GNSSTools.gpstobd09(116.314049758,40.069384452)
    print('%f,%f' % (ll[0],ll[1]))