from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
from hjn.mkNCHJN import envelope,mkDir
import numpy as np
import netCDF4 as nc
import copy
import geopandas as gpd
from osgeo import gdal, ogr, osr
import os

class maskClip():
    def __init__(self,data,latAtt,lonArr,step):

        self.dem = data
        self.latArr = latAtt
        self.lonArr = lonArr

        oriStep=np.abs((self.latArr[0]-self.latArr[-1])/(len(self.latArr)-1))
        range=int(np.round(step/oriStep,0))
        self.dem=self.dem[::range,::range]

        self.ltc = envelope(self.latArr[0], self.latArr[-1], self.lonArr[0], self.lonArr[-1])
        self.step = step

    def world2Pixel(self,ltc, x, y):
        """
        Uses a gdal geomatrix (gdal.GetGeoTransform()) to calculate
        the pixel location of a geospatial coordinate
        """
        ulX = ltc.w
        ulY = ltc.n
        xDist = self.step

        pixel = int((x - ulX) / xDist)
        line = int((ulY - y) / xDist)
        return (pixel, line)


    def getMask(self,geom,minX,maxY,minY,maxX):

        points = []
        pixels = []
        ulX, ulY = self.world2Pixel(self.ltc, minX, maxY)
        lrX, lrY = self.world2Pixel(self.ltc, maxX, minY)

        # Calculate the pixel size of the new image
        pxWidth = int(lrX - ulX)
        pxHeight = int(lrY - ulY)

        ltc1 = copy.copy(self.ltc)
        ltc1.n = maxY
        ltc1.w = minX

        pts = geom.boundary.xy
        for p in range(len(pts[0])):
            points.append((pts[0][p], pts[1][p]))
        for p in points:
            pixels.append(self.world2Pixel(ltc1, p[0], p[1]))
        rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
        rasterize = ImageDraw.Draw(rasterPoly)
        if len(pixels) > 1:
            rasterize.polygon(pixels, 0)

        mask = np.asarray(rasterPoly)


        # plt.imshow(mask)
        # plt.show()

        latOffset0 = int((self.ltc.n - maxY) / self.step)
        latOffset1 = self.dem.shape[0] - int((self.ltc.n - minY) / self.step)
        lonOffset0 = int((minX - self.ltc.w) / self.step)
        lonOffset1 = self.dem.shape[1] - int((maxX - self.ltc.w) / self.step)
        ndarray = np.pad(mask, ((latOffset0, latOffset1),
                                (lonOffset0, lonOffset1)), 'constant', constant_values=(1, 1))

        clip = copy.copy(self.dem)

        clip[ndarray != 0] = np.nan

        return clip



    def clip(self,shapefile_path,encoding='gb18030'):
        chly = gpd.GeoDataFrame.from_file(shapefile_path, encoding=encoding).geometry

        minX, maxX, minY, maxY = chly.bounds.min().minx,chly.bounds.max().maxx,chly.bounds.min().miny,chly.bounds.max().maxy
        maskArr=[]

        for j in range(len(chly)):
            geom = chly[j]
            if geom.geometryType() == 'Polygon':
                clip=self.getMask(geom, minX, maxY, minY, maxX)
                maskArr.append(clip)
            elif geom.geometryType() == "MultiPolygon":
                multiLayer = []
                for i in range(len(geom)):
                    geom1 = geom[i]
                    clip = self.getMask(geom1, minX, maxY, minY, maxX)
                    multiLayer.append(clip)

                multiLayer= np.asarray(multiLayer)
                clip = np.nanmax(multiLayer,axis=0)
                maskArr.append(clip)

        return maskArr

    def getMaskMask(self, geom, minX, maxY, minY, maxX):

        points = []
        pixels = []
        ulX, ulY = self.world2Pixel(self.ltc, minX, maxY)
        lrX, lrY = self.world2Pixel(self.ltc, maxX, minY)

        # Calculate the pixel size of the new image
        pxWidth = int(lrX - ulX)
        pxHeight = int(lrY - ulY)

        ltc1 = copy.copy(self.ltc)
        ltc1.n = maxY
        ltc1.w = minX

        pt = geom.boundary
        # print(pt)

        if pt.type == "LineString":
            pts = pt.xy
            for p in range(len(pts[0])):
                points.append((pts[0][p], pts[1][p]))
            for p in points:
                pixels.append(self.world2Pixel(ltc1, p[0], p[1]))
            rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
            rasterize = ImageDraw.Draw(rasterPoly)
            if len(pixels) > 1:
                rasterize.polygon(pixels, 0)

            mask = np.asarray(rasterPoly)

            latOffset0 = int((self.ltc.n - maxY) / self.step)
            latOffset1 = self.dem.shape[0] - int((self.ltc.n - minY) / self.step)
            lonOffset0 = int((minX - self.ltc.w) / self.step)
            lonOffset1 = self.dem.shape[1] - int((maxX - self.ltc.w) / self.step)
            ndarray = np.pad(mask, ((latOffset0, latOffset1),
                                    (lonOffset0, lonOffset1)), 'constant', constant_values=(1, 1))

            # clip = copy.copy(self.dem)
            # clip[ndarray != 0] = np.nan
            return mask
        else:
            # return
            masks = []

            for ptt in pt[:1]:
                pts = ptt.xy
                for p in range(len(pts[0])):
                    points.append((pts[0][p], pts[1][p]))
                for p in points:
                    pixels.append(self.world2Pixel(ltc1, p[0], p[1]))
                rasterPoly = Image.new("L", (pxWidth, pxHeight), 1)
                rasterize = ImageDraw.Draw(rasterPoly)
                if len(pixels) > 1:
                    rasterize.polygon(pixels, 0)

                mask = np.asarray(rasterPoly)
                masks.append(mask)
            masks = np.asarray(masks)
            masks = np.min(masks, axis=0)
            latOffset0 = int((self.ltc.n - maxY) / self.step)
            latOffset1 = self.dem.shape[0] - int((self.ltc.n - minY) / self.step)
            lonOffset0 = int((minX - self.ltc.w) / self.step)
            lonOffset1 = self.dem.shape[1] - int((maxX - self.ltc.w) / self.step)
            ndarray = np.pad(masks, ((latOffset0, latOffset1),
                                     (lonOffset0, lonOffset1)), 'constant', constant_values=(1, 1))

            clip = copy.copy(self.dem)
            clip[ndarray != 0] = np.nan
            return clip

    def clipMask(self,chlyTable):
        # chlyTable = gpd.GeoDataFrame.from_file(shapefile_path, encoding=encoding)
        chly = chlyTable.geometry
        minX, maxX, minY, maxY = chly.bounds.min().minx,chly.bounds.max().maxx,chly.bounds.min().miny,chly.bounds.max().maxy
        maskArr=[]

        for j in range(len(chly)):
            geom = chly.iloc[j]
            if geom.geometryType() == 'Polygon':
                clip=self.getMaskMask(geom, minX, maxY, minY, maxX)
                if not clip is None:
                    maskArr.append(clip)

            elif geom.geometryType() == "MultiPolygon":
                multiLayer = []
                for i in range(len(geom)):
                    geom1 = geom[i]
                    clip = self.getMaskMask(geom1, minX, maxY, minY, maxX)
                    multiLayer.append(clip)

                multiLayer= np.asarray(multiLayer)
                clip = np.nanmin(multiLayer,axis=0)
                if not clip is None:
                    maskArr.append(clip)

        return maskArr


class slope_aspect():
    def __init__(self,gridNew,dx, dy):
        self.gridNew = gridNew
        self.dx = dx
        self.dy = dy
        self.Sx, self.Sy = self.calcFiniteSlopes(gridNew, self.dx, self.dy)
    # 计算dx,dy
    def calcFiniteSlopes(self,elevGrid, dx, dy):
        Zbc = np.pad(elevGrid, ((1, 1), (1, 1)), "edge")
        Sx = (Zbc[1:-1, :-2] - Zbc[1:-1, 2:]) / (2 * dx)  # WE方向
        Sy = (Zbc[2:, 1:-1] - Zbc[:-2, 1:-1]) / (2 * dy)  # NS方向
        return Sx, Sy

    def calcFiniteAspect(self,Sx, Sy):

        Sx = Sx.astype(np.float)
        Sy = Sy.astype(np.float)
        aspect = np.degrees(np.arctan2(Sy, Sx))
        aspect1 = copy.copy(aspect)
        aspect1[aspect < 0] = 90 - aspect[aspect < 0]
        aspect1[aspect > 90] = 360.0 - aspect[aspect > 90] + 90.0
        aspect1[np.logical_and(aspect <= 90, aspect >= 0)] = 90.0 - aspect[np.logical_and(aspect <= 90, aspect >= 0)]
        aspect1[np.logical_and(Sx == 0, Sy == 0)] = -1
        return aspect1

    def getSlop(self):
        return np.degrees(np.arctan(np.sqrt(self.Sx ** 2 + self.Sy ** 2)))

    def getAspect(self):
        return self.calcFiniteAspect(self.Sx, self.Sy)


def Polygonize(mask,latArr,lonArr,outshp,EPSG=4326):
    driver = gdal.GetDriverByName("GTiff")
    im_bands = 1
    dataset = driver.Create("./tmp.tiff", mask.shape[1], mask.shape[0], im_bands, gdal.GDT_UInt16)
    im_geotrans = (lonArr[0], lonArr[1]-lonArr[0], 0, latArr[0], 0, latArr[1]-latArr[0])
    dataset.SetGeoTransform(im_geotrans)
    prj = osr.SpatialReference()
    prj.ImportFromEPSG(EPSG)
    dataset.SetProjection(prj.ExportToWkt())
    dataset.GetRasterBand(1).WriteArray(mask) 
    inband = dataset.GetRasterBand(1)
    mkDir(outshp)
    drv = ogr.GetDriverByName("ESRI Shapefile")
    if os.path.exists(outshp):
        drv.DeleteDataSource(outshp)
    Polygon = drv.CreateDataSource(outshp)
    Poly_layer = Polygon.CreateLayer(outshp, srs=prj,
                                     geom_type=ogr.wkbMultiPolygon)
    newField = ogr.FieldDefn('value', ogr.OFTReal)
    Poly_layer.CreateField(newField)
    gdal.FPolygonize(inband, None, Poly_layer, 0)
    Polygon.SyncToDisk()
    del Polygon
    os.remove("./tmp.tiff")

