# *-* coding=utf8
import numpy as np
import netCDF4 as nc
import datetime
import traceback
from dateutil.relativedelta import relativedelta
import copy
import os

class envelope():
	def __init__(self,n,s,w,e):
		self.n,self.s,self.w,self.e=n,s,w,e
	def __str__(self):
		return ("n:%s,s:%s,w:%s,e:%s"%(self.n,self.s,self.w,self.e))


areaNameDict = {"NEC": "东北","NCN": "华北","CCN": "华中","SCN": "华南","NWC": "西北","SWC": "西南","XJ": "新疆", "XZ": "西藏","CHN":"中国"}        
areaIdxDict = {"NEC": 0,"NCN": 1,"CCN": 2,"SCN": 3,"NWC": 4,"SWC": 5,"XJ": 6, "XZ": 7,"CHN":8}
LeftTopCornerCHN = np.asarray([{"area":"CHN", "evn":envelope(55, 15,72, 136), "CHarea":"中国"}])


LeftTopCornerPairArr = np.asarray([
#   //东北
    {"area":"NEC", "evn":envelope(55, 38,109, 136), "CHarea":"东北"},
#   //华北
    {"area":"NCN", "evn":envelope(43,31, 109,124), "CHarea":"华北"},
#     //华中
    {"area":"CCN", "evn":envelope(36,22, 108, 124), "CHarea":"华中"},
#     //华南
    {"area":"SCN", "evn":envelope(27, 15,104, 124), "CHarea":"华南"},
#     //西北
    {"area":"NWC", "evn":envelope(44,31, 88, 114), "CHarea":"西北"},
#     //西南
    {"area":"SWC", "evn":envelope(35, 20,96, 111), "CHarea":"西南"},
#     //新疆
    {"area":"XJ", "evn":envelope(50, 34,72, 97), "CHarea":"新疆"},
#     //西藏
    {"area":"XZ", "evn":envelope(37,25, 77, 101), "CHarea":"西藏"}])


LeftTopCornerPairArrClip = np.asarray([
#   //东北
    {"area":"NEC", "evn":envelope(55+10e-5, 38+10e-5, 109+10e-5, 136+10e-5), "CHarea":"东北"},
#   //华北
    {"area":"NCN", "evn":envelope(43+10e-5, 31+10e-5, 109+10e-5, 124+10e-5), "CHarea":"华北"},
#     //华中
    {"area":"CCN", "evn":envelope(36+10e-5, 22+10e-5, 108+10e-5, 124+10e-5), "CHarea":"华中"},
#     //华南
    {"area":"SCN", "evn":envelope(27+10e-5, 15+10e-5, 104+10e-5, 124+10e-5), "CHarea":"华南"},
#     //西北
    {"area":"NWC", "evn":envelope(44+10e-5, 31+10e-5, 88+10e-5, 114+10e-5), "CHarea":"西北"},
#     //西南
    {"area":"SWC", "evn":envelope(35+10e-5, 20+10e-5, 96+10e-5, 111+10e-5), "CHarea":"西南"},
#     //新疆
    {"area":"XJ", "evn":envelope(50+10e-5, 34+10e-5, 72+10e-5, 97+10e-5), "CHarea":"新疆"},
#     //西藏
    {"area":"XZ", "evn":envelope(37+10e-5,25+10e-5, 77+10e-5, 101+10e-5), "CHarea":"西藏"}])


LeftTopCornerPairArrSLL = np.asarray([
#   //大渡河
    {"area":"DDH", "evn":envelope(30.96, 28.96,101.21, 103.21)},
#   //贵阳
    {"area":"GY", "evn":envelope(27.08,26.08, 106.23,107.23)},
#     //长春
    {"area":"CC", "evn":envelope(44.4,43.4, 124.72, 125.72)},
#     //深圳
    {"area":"SZ", "evn":envelope(22.86, 22.38,113.76, 114.63)},
#     //天津
    {"area":"TJ", "evn":envelope(40.26,38.56, 116.69, 118.06)},
#     //黄山
    {"area":"HS", "evn":envelope(35, 25,113, 123)},
#     //华山
    {"area":"HUAS", "evn":envelope(36, 30,105, 115)},
#     //武汉
    {"area":"WH", "evn":envelope(31.37, 29.96,113.69, 115.08)},
#     //潍坊
    {"area":"WF", "evn":envelope(37.31, 35.70,118.17,120.0 )},
#     //川藏
    {"area":"CZ", "evn":envelope(33,28, 90, 105)}])
LeftTopCornerPairArrSLLnew = np.asarray([
#   //四川
    {"area":"SC", "evn":envelope(36,25,95,110)},
#     //吉林
    {"area":"JL", "evn":envelope(49,38,121,132)},
#     //广东
    {"area":"GD", "evn":envelope(27,19,109,118)},
#     //京津冀
    {"area":"JJJ", "evn":envelope(44,34,112,121)},
#     //安徽
    {"area":"AH", "evn":envelope(36,29,114,120)},
#     //陕西
    {"area":"SAX", "evn":envelope(41,31,104,113)},
#     //湖北
    {"area":"HB", "evn":envelope(35,28,108,117)},
#     //山东
    {"area":"SD", "evn":envelope(40,33,114,124)}])

class zClass():
    data_ = None
    name_ = None
    type_ = np.float32
    coordinate_ = None
    unit_ = None
    positive_ = None
    def __init__(self, data, name, type_, coordinate, unit,positive):
        self.data_, self.name_, self.type_, self.coordinate_, self.unit_, self.positive_ = data, name, type_, coordinate, unit,positive



class dataClass():
	data_ = None
	name_ = None
	type_ = np.float32
	coordinate_ = None
	unit_ = None
	valid_range_ = [-999,999]
	missing_value_ = np.NAN
	scale_factor_ = np.float32(1.0)
	add_offset_ = np.float32(0.0)

	def __init__(self,data, name, type_,coordinate, unit,missing_value=np.NAN, scale_factor=np.float32(1.0), add_offset=np.float32(0.0),valid_range=[-999,999]):
		self.data_, self.name_, self.type_, self.coordinate_, self.unit_ ,self.missing_value_ ,self.scale_factor_,self.add_offset_,self.valid_range_= data, name,type_, coordinate, unit,missing_value, scale_factor, add_offset, valid_range

	def print(self):
		print(self.data_, self.name_, self.type_, self.coordinate_, self.unit_,self.missing_value_,self.scale_factor_,self.add_offset_,self.valid_range_)
		
def mkNCCommonUni(output,dateTimeStart,dateTimeArr,isoArr,latArr,lonArr,dataClass4D=[],dataClass3D=[],dataClass2D=[],format='NETCDF4'):
    outputTmp = output+".tmp"
    dataset = nc.Dataset(outputTmp,'w',format=format) #'NETCDF4_CLASSIC')
    
    try:
        if not dateTimeArr is None and not dateTimeStart is None: 
            dataset.createDimension("time", len(dateTimeArr))
        if not isoArr is None:
            dataset.createDimension("isobaric", len(isoArr))
        
        dataset.createDimension("lat", len(latArr))
        dataset.createDimension("lon", len(lonArr))
    
        if not dateTimeArr is None and not dateTimeStart is None:
            dataset.createVariable("time", np.float32, ("time"), zlib=True)
        if not isoArr is None:
            dataset.createVariable("isobaric", np.float32, ("isobaric"), zlib=True)
        dataset.createVariable("lat", np.float64, ("lat"), zlib=True)
        dataset.createVariable("lon", np.float64, ("lon"), zlib=True)

        for e in dataClass2D:
            dataset.createVariable(e.name_, e.type_, tuple(["lat","lon"]), zlib=True)    

        for e in dataClass3D:
            dataset.createVariable(e.name_, e.type_, tuple(["time","lat","lon"]), zlib=True)

        for e in dataClass4D:
            dataset.createVariable(e.name_, e.type_, tuple(["time","isobaric","lat","lon"]), zlib=True)
        if not dateTimeArr is None and not dateTimeStart is None:
            dataset.variables["time"][:] = dateTimeArr
            dataset.variables["time"].units = 'minutes since %s'%(dateTimeStart.strftime("%Y-%m-%d %H:%M:%S"))
            dataset.variables["time"].calendar = 'gregorian'

        if not isoArr is None:
            dataset.variables["isobaric"][:] = isoArr
            dataset.variables["isobaric"].units="hPa"
            dataset.variables["isobaric"].positive="up"
        
        dataset.variables["lat"][:] = latArr
        dataset.variables['lat'].units = 'degrees_north'
    
        dataset.variables["lon"][:] = lonArr
        dataset.variables['lon'].units = 'degrees_east'
        
        for e in dataClass2D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_
    
        for e in dataClass3D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_

        for e in dataClass4D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_

        #dataset.close()
    except Exception as ex:
        print(ex)
        print(latArr.shape,lonArr.shape,e.data_.shape)
        print(traceback.format_exc())
        #dataset.close()
    finally:
        dataset.close()
        os.renames(outputTmp,output)

def mkNCCommonUni_multiISO(output, dateTimeStart, dateTimeArr, isoArr, latArr, lonArr, dataClass4D=[], dataClass3D=[],
                  dataClass2D=[], format='NETCDF4'):
    dataset = nc.Dataset(output, 'w', format=format)  # 'NETCDF4_CLASSIC')

    try:
        if not dateTimeArr is None and not dateTimeStart is None:
            dataset.createDimension("time", len(dateTimeArr))


        if not isoArr is None:
            for iso in isoArr:
                dataset.createDimension(iso.name_, len(iso.data_))

        dataset.createDimension("lat", len(latArr))
        dataset.createDimension("lon", len(lonArr))

        if not dateTimeArr is None and not dateTimeStart is None:
            dataset.createVariable("time", np.float32, ("time"), zlib=True)
            
        if not isoArr is None:
            for iso in isoArr:
                dataset.createVariable(iso.name_, iso.type_, iso.coordinate_, zlib=True)

        dataset.createVariable("lat", np.float64, ("lat"), zlib=True)
        dataset.createVariable("lon", np.float64, ("lon"), zlib=True)

        for e in dataClass2D:
            dataset.createVariable(e.name_, e.type_, tuple(e.coordinate_), zlib=True)

        for e in dataClass3D:
            dataset.createVariable(e.name_, e.type_, tuple(e.coordinate_), zlib=True)

        for e in dataClass4D:
            dataset.createVariable(e.name_, e.type_, tuple(e.coordinate_), zlib=True)
        if not dateTimeArr is None and not dateTimeStart is None:
            dataset.variables["time"][:] = dateTimeArr
            dataset.variables["time"].units = 'minutes since %s' % (dateTimeStart.strftime("%Y-%m-%d %H:%M:%S"))
            dataset.variables["time"].calendar = 'gregorian'

        if not isoArr is None:
            for iso in isoArr:
                dataset.variables[iso.name_][:] = iso.data_
                dataset.variables[iso.name_].units = iso.unit_
                dataset.variables[iso.name_].positive = iso.positive_

        dataset.variables["lat"][:] = latArr
        dataset.variables['lat'].units = 'degrees_north'

        dataset.variables["lon"][:] = lonArr
        dataset.variables['lon'].units = 'degrees_east'

        for e in dataClass2D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_

        for e in dataClass3D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_

        for e in dataClass4D:
            dataset.variables[e.name_][:] = e.data_
            dataset.variables[e.name_].units = e.unit_
            dataset.variables[e.name_].valid_range = e.valid_range_
            if not "3" in format:
                dataset.variables[e.name_].coordinate = e.coordinate_
            dataset.variables[e.name_].missing_value = e.missing_value_
            dataset.variables[e.name_].scale_factor = e.scale_factor_
            dataset.variables[e.name_].add_offset = e.add_offset_

        # dataset.close()
    except Exception as ex:
        print(ex)
        print(latArr.shape, lonArr.shape, e.data_.shape)
        print(traceback.format_exc())
        # dataset.close()
    finally:
        dataset.close()


def clip(data, ltc, lat0, lon0, step):
    latIdx0 = int((lat0 - ltc.n) / step+ 0.5)
    latIdx1 = int((lat0 - ltc.s) / step+ 0.5)
    lonIdx0 = int((ltc.w - lon0) / step+ 0.5)
    lonIdx1 = int((ltc.e - lon0) / step+ 0.5)
    data = data[...,latIdx0:latIdx1+1, lonIdx0:lonIdx1+1]
    return data

def clip2(data, ltc, latArr, lonArr, step,isPad=False):
    latIdx0 = int((latArr[0] - ltc.n) / step+ 0.5)
    latIdx1 = int((latArr[0] - ltc.s) / step+ 0.5)
    lonIdx0 = int((ltc.w - lonArr[0]) / step+ 0.5)
    lonIdx1 = int((ltc.e - lonArr[0]) / step+ 0.5)
    if isPad:
        if latArr[latIdx0]<ltc.n and latIdx0>0:
            latIdx0 -=1
        if latArr[latIdx1]>ltc.s and latIdx1< (len(latArr)-1):
            latIdx1 +=1
        if lonArr[lonIdx0] > ltc.w and lonIdx0 > 0:
            lonIdx0 -= 1
        if lonArr[lonIdx1] < ltc.e and lonIdx1 < (len(lonArr) - 1):
            lonIdx1 += 1

    data = data[...,latIdx0:latIdx1+1, lonIdx0:lonIdx1+1]
    return data

def clipLat(data, ltc, step,isPad=False):
    latIdx0 = int((data[0] - ltc.n) / step+ 0.5)
    latIdx1 = int((data[0] - ltc.s) / step+ 0.5)
    if isPad:
        if data[latIdx0]<ltc.n and latIdx0>0:
            latIdx0 -=1
        if data[latIdx1]>ltc.s and latIdx1< (len(data)-1):
            latIdx1 +=1
    data = data[latIdx0:latIdx1+1]
    return data

def clipLon(data, ltc, step,isPad=False):
    lonIdx0 = int((ltc.w - data[0]) / step+ 0.5)
    lonIdx1 = int((ltc.e - data[0]) / step+ 0.5)
    if isPad:
        if data[lonIdx0]>ltc.w and lonIdx0>0:
            lonIdx0 -=1
        if data[lonIdx1]<ltc.e and lonIdx1< (len(data)-1):
            lonIdx1 +=1
    data = data[lonIdx0:lonIdx1+1]
    return data

def totalTimes(delta,second):
    return (delta.days*24*3600+delta.seconds)//second

#def timeSeq(start,end,secInter):
#    times=totalTimes((end-start),secInter)
#    return list(map(lambda x:start+relativedelta(seconds=x*secInter),range(times)))

def timeSeq(start,end,secInter,endPoint=True):
    times=totalTimes((end-start),secInter)
    end = 1 if endPoint else 0
    return list(map(lambda x:start+relativedelta(seconds=x*secInter),range(times+end)))

def UV2WSWD(U,V):
    ws = np.sqrt(np.square(U) + np.square(V))
    wd = (np.degrees(np.arctan2(-U, -V))+ 360)%360
    return ws,wd

def WSWD2UV(ws,wd):
    u=- ws*np.sin(np.radians(wd))
    v=- ws*np.cos(np.radians(wd))
    return u,v

def test():
    print("test")

def normalNC(data):
    mx=np.nanmax(data)
    mn = np.nanmin(data)
    rangeV=mx-mn
    scale = rangeV/254
    offset = (mx+mn)/2
    data1=(data - offset)/scale
    data1[np.isnan(data1)] = -128
    return data1,scale,offset

def SunAngle(UTC, lat, lon, TimeZone = 0):    
    year, DOY, hour = UTC.timetuple().tm_year, UTC.timetuple().tm_yday, UTC.timetuple().tm_hour
    min, second = UTC.timetuple().tm_min, UTC.timetuple().tm_sec
    N0 = 79.6764 + 0.2422 * (year - 1985) - int((year - 1985) / 4.0)
    sitar = 2 * np.pi * (DOY - N0) / 365.2422
    ED1 = 0.3723 + 23.2567 * np.sin(sitar) + 0.1149 * np.sin(2 * sitar) - 0.1712 * np.sin(3 * sitar) - 0.758 * np.cos(sitar) + 0.3656 * np.cos(2 * sitar) + 0.0201 * np.cos(3 * sitar)
    ED = ED1 * np.pi / 180
    dLon = lon - TimeZone * 15.0
    Et = 0.0028 - 1.9857 * np.sin(sitar) + 9.9059 * np.sin(2 * sitar) - 7.0924 * np.cos(
        sitar) - 0.6882 * np.cos(2 * sitar)
    gtdt1 = hour + min / 60.0 + second / 3600.0 + dLon / 15

    gtdt = gtdt1 + Et / 60.0
    dTimeAngle1 = 15.0 * (gtdt - 12)
    dTimeAngle = dTimeAngle1 * np.pi / 180

    latitudeArc = lat * np.pi / 180
    HeightAngleArc = np.arcsin(np.sin(latitudeArc) * np.sin(ED) + np.cos(latitudeArc) * np.cos(ED) * np.cos(dTimeAngle))
    HeightAngle = HeightAngleArc * 180 / np.pi
    return HeightAngle

class clip_and_mosaic():
    def __init__(self,mat,patch,overlap):
        self.mat = mat
        self.patch = patch
        self.overlap = overlap
        center = patch - 2 * overlap
        self.center = center
        self.latRange = int(np.ceil(mat.shape[0]/center))
        lastPaddingLat = self.latRange*center-mat.shape[0]
        self.lonRange = int(np.ceil(mat.shape[1] / center))
        lastPaddingLon = self.lonRange * center - mat.shape[1]
        self.padMat =np.pad(mat,((overlap,lastPaddingLat+overlap),(overlap,lastPaddingLon+overlap)),'constant', constant_values=(0,0))
        self.outMat = np.zeros(self.padMat.shape)

    def clip(self):
        imgList = []
        for i in range(self.latRange):
            for j in range(self.lonRange):
                clipMat = self.padMat[self.center*i:self.center*(i+1)+2*overlap,self.center*j:self.center*(j+1)+2*overlap]
                imgList.append(clipMat)
                # plt.subplot(self.latRange,self.lonRange,j+self.lonRange*i+1)
                # plt.imshow(clipMat)
        return imgList

    def mosaic(self,imgList):
        for i in range(self.latRange):
            for j in range(self.lonRange):
                self.outMat[self.center*i:self.center*(i+1)+2*overlap,self.center*j:self.center*(j+1)+2*overlap] = imgList[j+self.lonRange*i]
        finalMat = self.outMat[overlap:overlap+self.mat.shape[0],overlap:overlap+self.mat.shape[1]]
        return finalMat

# calculate sun angle
def calSunAngle(localTime, TimeZone, lat, lon):
    lon[lon<0] +=360
    year = localTime.year
    month = localTime.month
    day = localTime.day
    hour = localTime.hour
    min = localTime.minute
    sec = localTime.second
    DOY = localTime.timetuple().tm_yday

    N0 = int(79.6764 + 0.2422 * (year - 1985) - ((year - 1985) / 4.0))

    sitar = 2 * np.pi * (DOY - N0) / 365.2422
    ED1 = 0.3723 + 23.2567 * np.sin(sitar) + 0.1149 * np.sin(2 * sitar) - 0.1712 * np.sin(3 * sitar) - 0.758 * np.cos(
        sitar) + 0.3656 * np.cos(2 * sitar) + 0.0201 * np.cos(3 * sitar)
    ED = ED1 * np.pi / 180
    # //    #ED本身有符号

    dLon = copy.copy(lon)

    dLon[np.logical_and(lon >= 0, TimeZone == -13)] = lon[np.logical_and(lon >= 0, TimeZone == -13)] - (
                np.floor((lon[np.logical_and(lon >= 0, TimeZone == -13)] * 10 - 75) / 150) + 1) * 15.0
    dLon[np.logical_and(lon >= 0, TimeZone != -13)] = lon[np.logical_and(lon >= 0, TimeZone != -13)] - TimeZone * 15.0

    dLon[np.logical_and(lon < 0, TimeZone == -13)] = (np.floor(
        (lon[np.logical_and(lon < 0, TimeZone == -13)] * 10 - 75) / 150) + 1) * 15.0 - lon[
                                                         np.logical_and(lon < 0, TimeZone == -13)]
    dLon[np.logical_and(lon < 0, TimeZone != -13)] = TimeZone * 15.0 - lon[np.logical_and(lon < 0, TimeZone != -13)]

    # //    #时差
    Et = 0.0028 - 1.9857 * np.sin(sitar) + 9.9059 * np.sin(2 * sitar) - 7.0924 * np.cos(sitar) - 0.6882 * np.cos(
        2 * sitar)
    gtdt1 = hour + min / 60.0 + sec / 3600.0 + dLon / 15
    # //    #地方时
    gtdt = gtdt1 + Et / 60.0
    dTimeAngle1 = 15.0 * (gtdt - 12)
    dTimeAngle = dTimeAngle1 * np.pi / 180

    latitudeArc = lat * np.pi / 180

    HeightAngleArc = np.arcsin(np.sin(latitudeArc) * np.sin(ED) + np.cos(latitudeArc) * np.cos(ED) * np.cos(dTimeAngle))

    CosAzimuthAngle = (np.sin(HeightAngleArc) * np.sin(latitudeArc) - np.sin(ED)) / np.cos(HeightAngleArc) / np.cos(
        latitudeArc)
    AzimuthAngleArc = np.arccos(CosAzimuthAngle)
    HeightAngle = HeightAngleArc * 180 / np.pi
    ZenithAngle = 90 - HeightAngle
    AzimuthAngle1 = AzimuthAngleArc * 180 / np.pi

    AzimuthAngle = copy.copy(AzimuthAngle1)
    AzimuthAngle[dTimeAngle < 0] = 180 - AzimuthAngle1[dTimeAngle < 0]
    AzimuthAngle[dTimeAngle >= 0] = 180 + AzimuthAngle1[dTimeAngle >= 0]

    # //    println( s"太阳天顶角(deg):${ZenithAngle} 高度角(deg)：${HeightAngle} 方位角(deg)：$AzimuthAngle")
    return ZenithAngle, HeightAngle, AzimuthAngle

def mkDir(path):
    if "." in path:
        os.makedirs(os.path.dirname(path),exist_ok=True)
    else:
        os.makedirs(path, exist_ok=True)


def expend(data,latArr,lonArr,dim=2,fill_value=np.nan,areaLtc=None):
    if areaLtc is None:
        N = LeftTopCornerPairArr[0]["evn"].n
        S = LeftTopCornerPairArr[3]["evn"].s
        W = LeftTopCornerPairArr[6]["evn"].w
        E = LeftTopCornerPairArr[0]["evn"].e
    else:
        N = areaLtc.n
        S = areaLtc.s
        W = areaLtc.w
        E = areaLtc.e

    latOffset = int((N - latArr[0]) / 0.01)
    latOffsetDown = int((latArr[-1] - S) / 0.01)
    lonOffset = int((lonArr[0] - W) / 0.01)
    lonOffsetRight = int((E - lonArr[-1]) / 0.01)
    appendLat = np.asarray(list(map(lambda x: latArr[0] + x * 0.01, range(1, latOffset + 2)))[::-1])
    appendLatDown = np.asarray(list(map(lambda x: latArr[-1] - x * 0.01, range(1, latOffsetDown + 2))))
    latArr = np.r_[appendLat, latArr]
    latArr = np.r_[latArr, appendLatDown]
    appendLon = np.asarray(list(map(lambda x: lonArr[0] - x * 0.01, range(1, lonOffset + 2)))[::-1])
    appendLonRight = np.asarray(list(map(lambda x: lonArr[-1] + x * 0.01, range(1, lonOffsetRight + 2))))
    lonArr = np.r_[appendLon, lonArr]
    lonArr = np.r_[lonArr, appendLonRight]

    if latOffset<0:
        latOffset=0
    if latOffsetDown < 0:
        latOffsetDown = 0
    if lonOffset < 0:
        lonOffset = 0
    if lonOffsetRight < 0:
        lonOffsetRight = 0

    if dim==2:
        data = np.pad(data, ((latOffset+1 , latOffsetDown+1 ), (lonOffset+1 , lonOffsetRight+1)),constant_values=fill_value)
    elif dim==3:
        data = np.pad(data, ((0, 0), (latOffset+1, latOffsetDown+1), (lonOffset+1, lonOffsetRight+1)), constant_values=fill_value)
    elif dim==4:
        data = np.pad(data, ((0, 0),(0, 0), (latOffset+1, latOffsetDown+1), (lonOffset+1, lonOffsetRight+1)), constant_values=fill_value)
    return data,latArr,lonArr


def checkNC(path):
    with nc.Dataset(path) as dataNC:
        for e in list(dataNC.variables):
            dataNC[e][:]

def cropDF(df,evn):
    return df[np.logical_and.reduce([df["Lat"]>evn.s,df["Lat"]<evn.n,df["Lon"]>evn.w,df["Lon"]<evn.e])]


