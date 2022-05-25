
import numpy as np
import copy
import os
import datetime

def bilinear(y,  x, yul, xul, vul,yur,  xur, vur, ydl, xdl, vdl, ydr,  xdr,vdr):
    u = linear(x, xul, vul, xur, vur)
    yu = linear(x, xul, yul, xur, yur)
    b = linear(x, xdl, vdl, xdr, vdr)
    yb = linear(x, xdl, ydl, xdr, ydr)
    v = linear(y, yu, u, yb, b)
    return v


def linear(x, xl, vl0, xr, vr0):
    vl=vl0
    vr=vr0
    if vl == vr:
        v=vl
    else:
        dxl = x - xl
        drl = xr - xl
        v = dxl * (vr - vl) / drl + vl
    return v

def getPoint3D(pre,df,lat0,lon0,resolution,decimal=1):
   
    latIdx = ((lat0 - df["Lat"]) / resolution + 0.5).astype(np.int64)
    lonIdx = ((df["Lon"] - lon0) / resolution + 0.5).astype(np.int64)
    return pre[:, latIdx, lonIdx].round(decimals=decimal)


def getPoint2D(pre, df, lat0, lon0, resolution, decimal=1):
    latIdx = ((lat0 - df["Lat"]) / resolution + 0.5).astype(np.int64)
    lonIdx = ((df["Lon"] - lon0) / resolution + 0.5).astype(np.int64)
    return pre[latIdx, lonIdx].round(decimals=decimal)

def getPoint(pre, df, lat0, lon0, resolution, decimal=1):
    latIdx = ((lat0 - df["Lat"]) / resolution + 0.5).astype(np.int64)
    lonIdx = ((df["Lon"] - lon0) / resolution + 0.5).astype(np.int64)
    return pre[...,latIdx, lonIdx].round(decimals=decimal)

def getPointBilinear3D(preData,df1,latArr,lonArr,decimal=2):
    df=copy.copy(df1)
    resolution=np.abs((latArr[0]-latArr[-1])/(len(latArr)-1))
    latIdxN = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)
    lonIdxW = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)

    latIdxS = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)+1
    lonIdxE = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)+1

    df["LatN"] = latArr[latIdxN]
    df["LonW"] = lonArr[lonIdxW]
    df["valNW"] = preData[:, latIdxN, lonIdxW]

    df["LatS"] = latArr[latIdxS]
    df["LonE"] = lonArr[lonIdxE]
    df["valSE"] = preData[:, latIdxS, lonIdxE]
    df["valNE"] = preData[:, latIdxN, lonIdxE]
    df["valSW"] = preData[:, latIdxS, lonIdxW]
    return df.apply(
                lambda x:np.round(bilinear(x["Lat"], x["Lon"], x["LatN"], x["LonW"], x["valNW"], x["LatN"], x["LonE"], x["valNE"], x["LatS"],
                                   x["LonW"], x["valSW"], x["LatS"], x["LonE"], x["valSE"]),decimals=decimal), axis=1)


def getPointBilinear2D(preData,df1,latArr,lonArr,decimal=2):
    df=copy.copy(df1)
    resolution=np.abs((latArr[0]-latArr[-1])/(len(latArr)-1))
    latIdxN = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)
    lonIdxW = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)

    latIdxS = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)+1
    lonIdxE = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)+1

    df["LatN"] = latArr[latIdxN]
    df["LonW"] = lonArr[lonIdxW]
    df["valNW"] = preData[latIdxN, lonIdxW]

    df["LatS"] = latArr[latIdxS]
    df["LonE"] = lonArr[lonIdxE]
    df["valSE"] = preData[ latIdxS, lonIdxE]
    df["valNE"] = preData[ latIdxN, lonIdxE]
    df["valSW"] = preData[ latIdxS, lonIdxW]
    return df.apply(
                lambda x:np.round(bilinear(x["Lat"], x["Lon"], x["LatN"], x["LonW"], x["valNW"], x["LatN"], x["LonE"], x["valNE"], x["LatS"],
                                   x["LonW"], x["valSW"], x["LatS"], x["LonE"], x["valSE"]),decimals=decimal), axis=1)
def getPointBilinear(preData,df1,latArr,lonArr,decimal=2):
    df=copy.copy(df1)
    resolution=np.abs((latArr[0]-latArr[-1])/(len(latArr)-1))
    latIdxN = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)
    lonIdxW = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)

    latIdxS = ((latArr[0] - df["Lat"]) / resolution).astype(np.int64)+1
    lonIdxE = ((df["Lon"] - lonArr[0]) / resolution).astype(np.int64)+1

    df["LatN"] = latArr[latIdxN]
    df["LonW"] = lonArr[lonIdxW]
    df["valNW"] = preData[..., latIdxN, lonIdxW]

    df["LatS"] = latArr[latIdxS]
    df["LonE"] = lonArr[lonIdxE]
    df["valSE"] = preData[..., latIdxS, lonIdxE]
    df["valNE"] = preData[..., latIdxN, lonIdxE]
    df["valSW"] = preData[..., latIdxS, lonIdxW]
    return df.apply(
                lambda x:np.round(bilinear(x["Lat"], x["Lon"], x["LatN"], x["LonW"], x["valNW"], x["LatN"], x["LonE"], x["valNE"], x["LatS"],
                                   x["LonW"], x["valSW"], x["LatS"], x["LonE"], x["valSE"]),decimals=decimal), axis=1)



def classify10min(pre0):
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.1] = 0
    pre[np.logical_and(pre0 >= 0.1, pre0 <= 0.5)] = 1
    pre[np.logical_and(pre0 > 0.5, pre0 <= 1)] = 2
    pre[np.logical_and(pre0 > 1, pre0 <= 2)] = 3
    pre[np.logical_and(pre0 > 2, pre0 <= 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre

def classify30min(pre0):
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.1] = 0
    pre[np.logical_and(pre0 >= 0.1, pre0 <= 2)] = 1
    pre[np.logical_and(pre0 > 2, pre0 <= 4)] = 2
    pre[np.logical_and(pre0 > 4, pre0 <= 10)] = 3
    pre[np.logical_and(pre0 > 10, pre0 <= 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre

def classify1h(pre0):
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.1] = 0
    pre[np.logical_and(pre0 >= 0.1, pre0 <= 2.5)] = 1
    pre[np.logical_and(pre0 > 2.5, pre0 <= 8)] = 2
    pre[np.logical_and(pre0 > 8, pre0 <= 16)] = 3
    pre[np.logical_and(pre0 > 16, pre0 <= 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre

# classify 3h
def classify3h(pre0):
    pre = copy.deepcopy(pre0)
    pre[pre0 < 0.1] = 0
    pre[np.logical_and(pre0 >= 0.1, pre0 <= 3)] = 1
    pre[np.logical_and(pre0 > 3, pre0 <= 10)] = 2
    pre[np.logical_and(pre0 > 10, pre0 <= 20)] = 3
    pre[np.logical_and(pre0 > 20, pre0 <= 9990)] = 4
    pre[pre0 > 9990] = -1
    pre[np.isnan(pre0)] = -1
    return pre

def degMinSectoDeg(a):
    deg = int(a.split("°")[0])
    sec = int(a.split("'")[-1][:-1])
    min = int(a.replace(f"{deg}°","").replace(f"'{sec}\"",""))
    return deg+min/60+sec/3600

def normal(data, min=None, max=None):
    if max is None:
        max = np.max(data)
    if min is None:
        min = np.min(data)
    rangeLat = max-min
    dataB = (data - min) / rangeLat
    return dataB

def mkDir(path):
    if "." in path:
        os.makedirs(os.path.dirname(path),exist_ok=True)
    else:
        os.makedirs(path, exist_ok=True)

def options():
    import argparse
    parser = argparse.ArgumentParser(description='hjn')
    parser.add_argument('--times', type=str, default='2018060700,2018060700')
    parser.add_argument('--isDebug',action='store_true',default=False)
    config= parser.parse_args()
    config.times = config.times.split(",")
    if len(config.times) == 1:
        config.times = [config.times[0], config.times[0]]
    config.times = [datetime.datetime.strptime(config.times[0], "%Y%m%d%H%M"),
                    datetime.datetime.strptime(config.times[1], "%Y%m%d%H%M")]

    return config

class Evaluate():
    def __init__(self,num_class):
        self.num_class = num_class
        self.confusion_matrix = np.zeros((self.num_class,)*2)

    def Mean_Intersection_over_Union(self):
        MIoU = np.diag(self.confusion_matrix) / (
                np.sum(self.confusion_matrix, axis=1) + np.sum(self.confusion_matrix, axis=0) -
                np.diag(self.confusion_matrix))
        MIoU = np.nanmean(MIoU)
        return MIoU

    def _generate_matrix(self, gt_image, pre_image):
        mask = (gt_image >= 0) & (gt_image < self.num_class)
        label = self.num_class * gt_image[mask].astype('int') + pre_image[mask]
        count = np.bincount(label, minlength=self.num_class**2)
        confusion_matrix = count.reshape(self.num_class, self.num_class)
        return confusion_matrix

    def add_batch(self, gt_image, pre_image):
        assert gt_image.shape == pre_image.shape
        self.confusion_matrix += self._generate_matrix(gt_image, pre_image)
