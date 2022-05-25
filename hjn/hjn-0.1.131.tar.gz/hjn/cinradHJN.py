import numpy as np
import netCDF4 as nc
import os
import datetime as dt
import bz2
import time
from dateutil.relativedelta import relativedelta
import pandas as pd
import urllib

# Author:hujunnan

np.set_printoptions(suppress=True)


def pad2D(data, col):
    return np.asarray(list(map(lambda x: x + ([np.nan] * (col - len(x))), data)))


def pad3D(data, radialMax, distance):
    tmp = list(map(lambda x: x + ([[np.nan] * distance] * (radialMax - len(x))), data))
    for i in range(len(tmp)):
        tmp[i] = pad2D(tmp[i], distance)
    return np.asarray(tmp)


class readCinrad():
    def __init__(self, path):
        self.path=path
        self.datetime = 0
        self.radarID=path.split("_")[3]
        self.type = path.split("_")[7]
        if ".bz2" in path:
            self.unzipBZ2()
        self.fi = open(self.path, "rb")
        self.Cut_Number = 0
        self.Log_Resolution = 0
        self.Doppler_Resolution = 0
        self.isDuelDict = {
            True: "双",
            False: "单"
        }
        self.isDual=False

    def seconds2datetime(self,seconds):
        return dt.datetime.strptime(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(seconds)), "%Y-%m-%d %H:%M:%S")

    def unzipBZ2(self):
        f = open(file=self.path, mode='rb')
        un = f.read()
        f.close()
        username = bz2.decompress(un)
        os.makedirs("./tmp",exist_ok=True)
        self.path=os.path.join("./tmp",os.path.basename(self.path).replace(".bz2",""))
        with open(self.path, 'wb')as fp:
            fp.write(username)

    def parse_GENERIC_HEADER(self):
        # 站点参数
        GENERIC_HEADER = np.dtype(
            {'names': ['Magic_Number', 'Major_Version', 'Minor_Version', 'Generic_Type', 'Product_Type', 'reserve'],
             'formats': ['i', 'h', 'h', 'i', 'i', 'S16']})
        [Magic_Number, Major_Version, Minor_Version, Generic_Type, Product_Type, _] = \
            np.fromfile(file=self.fi, dtype=GENERIC_HEADER, count=1, sep='')[0]
        print(Magic_Number, Major_Version, Minor_Version, Generic_Type, Product_Type)

    def parse_SITE_CONFIG(self):
        # 站点参数
        SITE_CONFIG = np.dtype(
            {'names': ['Site_Code', 'Site_Name', 'Latitude', 'Longitude', 'Antenna_Height', 'Ground_Height',
                       'Frequency', 'Beam_Width_Hori', 'Beam_Width_Vert', 'RDA_Version', 'Radar_Type', 'reserve'],
             'formats': ['S8', 'S32', 'f', 'f', 'i', 'i', 'f', 'f', 'f', 'i', 'h', 'S54']})
        [Site_Code, Site_Name, Latitude, Longitude, Antenna_Height, Ground_Height, Frequency, Beam_Width_Hori,
         Beam_Width_Vert, RDA_Version, Radar_Type, _] = np.fromfile(file=self.fi, dtype=SITE_CONFIG, count=1, sep='')[0]
        print(Site_Code, Site_Name, Latitude, Longitude, Antenna_Height, Ground_Height, Frequency, Beam_Width_Hori,
              Beam_Width_Vert, RDA_Version, Radar_Type)

    def parse_TASK_CONFIG(self):
        # //TASK CONFIG
        TASK_CONFIG = np.dtype(
            {'names': ['Task_Name', ' Task_Description', 'Polarization_Type', 'Scan_Type', 'Pulse_Width',
                       'Scan_Start_Time', 'Cut_Number', 'Horizontal_Noise', 'Vertical_Noise', 'Horizontal_Calibration',
                       'Vertical_Calibration', 'Horizontal_Noise_Temperature', 'Vertical_Noise_Temperature',
                       'ZDR_Calibration',
                       'PHIDP_Calibration', 'LDR_Calibration', 'reserve'],
             'formats': ['S32', 'S128', 'i', 'i', 'i', 'i', 'i', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'S40']})
        [Task_Name, Task_Description, Polarization_Type, Scan_Type, Pulse_Width, Scan_Start_Time, Cut_Number,
         Horizontal_Noise, Vertical_Noise, Horizontal_Calibration, Vertical_Calibration, Horizontal_Noise_Temperature,
         Vertical_Noise_Temperature, ZDR_Calibration, PHIDP_Calibration, LDR_Calibration, _] = \
            np.fromfile(file=self.fi, dtype=TASK_CONFIG, count=1, sep='')[0]

        self.datetime=self.seconds2datetime(Scan_Start_Time)
        # //系统LDR标定偏差
        # in.readStringHJN(40)
        # //保留字段
        #
        self.Cut_Number = Cut_Number
        if "dual" in str(Task_Description):
            self.isDual = True
        else:
            self.isDual = False
        print(Task_Name, Task_Description)
        print(Polarization_Type, Scan_Type, Pulse_Width, Scan_Start_Time, Cut_Number, Horizontal_Noise, Vertical_Noise,
              Horizontal_Calibration,
              Vertical_Calibration, Horizontal_Noise_Temperature, Vertical_Noise_Temperature, ZDR_Calibration,
              PHIDP_Calibration, LDR_Calibration)

        print("%s偏振" % (self.isDuelDict[self.isDual]))

    def parse_read_CUT_CONFIG(self):
        CUT_CONFIG1 = np.dtype(
            {'names': ['Process_Mode', 'Wave_Form', 'PRF_1', 'PRF_2', 'Dealiasing_Mode', 'Azimuth',
                       'Elevation', 'Start_Angle', 'End_Angle', 'Angular_Resolution', 'Scan_Speed',
                       'Log_Resolution', 'Doppler_Resolution', 'Maximum_Range1', 'Maximum_Range2', 'Start_Range',
                       'Sample_1', 'Sample_2', 'Phase_Mode', 'Atmospheric_Loss', 'Nyquist_Speed'],
             'formats': ['i', 'i', 'f', 'f', 'i', 'f', 'f', 'f', 'f', 'f', 'f', 'i', 'i', 'i', 'i', 'i', 'i',
                         'i', 'i', 'f', 'f']})
        [Process_Mode, Wave_Form, PRF_1, PRF_2, Dealiasing_Mode, Azimuth, Elevation, Start_Angle,
         End_Angle, Angular_Resolution, Scan_Speed, Log_Resolution, Doppler_Resolution, Maximum_Range1, Maximum_Range2,
         Start_Range, Sample_1, Sample_2, Phase_Mode, Atmospheric_Loss, Nyquist_Speed] = \
            np.fromfile(file=self.fi, dtype=CUT_CONFIG1, count=1, sep='')[0]
        print("扫描字块 Process_Mode:", Process_Mode, "Wave_Form:", Wave_Form, "PRF_1:", PRF_1, "PRF_2:", PRF_2,
              "Dealiasing_Mode:", Dealiasing_Mode, "Azimuth:", Azimuth, "Elevation:", Elevation, "Start_Angle:",
              Start_Angle, "End_Angle:", End_Angle, "Angular_Resolution:", Angular_Resolution, "Scan_Speed:",
              Scan_Speed, "Log_Resolution:", Log_Resolution, "Doppler_Resolution:", Doppler_Resolution,
              "Maximum_Range1:",
              Maximum_Range1, "Maximum_Range2:", Maximum_Range2, "Start_Range:", Start_Range, "Sample_1:", Sample_1,
              "Sample_2:", Sample_2, "Phase_Mode:", Phase_Mode, "Atmospheric_Loss:", Atmospheric_Loss, "Nyquist_Speed:",
              Nyquist_Speed)

        self.Log_Resolution = Log_Resolution
        self.Doppler_Resolution = Doppler_Resolution
        CUT_CONFIG2 = np.dtype(
            {'names': ['Moments_Mask', 'Moments_Size_Mask', 'Misc_Filter_Mask', 'SQI_Threshold', 'SIG_Threshold',
                       'CSR_Threshold',
                       'LOG_Threshold', 'CPA_Threshold', 'PMI_Threshold', 'DPLOG_Threshold',
                       'Thresholds_r', 'dBT_Mask', 'dBZ_Mask', 'Velocity_Mask', 'Spectrum_Width_Mask', 'DP_Mask',
                       'Mask_Reserved', 'Scan_Sync',
                       'Direction'],
             'formats': ['q', 'q', 'i', 'f', 'f', 'f', 'f', 'f', 'f', 'f', 'S4', 'i', 'i', 'i', 'i', 'i',
                         'S12', 'i', 'i']})
        [Moments_Mask, Moments_Size_Mask, Misc_Filter_Mask, SQI_Threshold, SIG_Threshold, CSR_Threshold,
         LOG_Threshold, CPA_Threshold, PMI_Threshold, DPLOG_Threshold,
         Thresholds_r, dBT_Mask, dBZ_Mask, Velocity_Mask, Spectrum_Width_Mask, DP_Mask, Mask_Reserved, Scan_Sync,
         Direction] = \
            np.fromfile(file=self.fi, dtype=CUT_CONFIG2, count=1, sep='')[0]

        print(Moments_Mask, Moments_Size_Mask, Misc_Filter_Mask, SQI_Threshold, SIG_Threshold, CSR_Threshold,
              LOG_Threshold, CPA_Threshold, PMI_Threshold, DPLOG_Threshold,
              Thresholds_r, dBT_Mask, dBZ_Mask, Velocity_Mask, Spectrum_Width_Mask, DP_Mask, Mask_Reserved, Scan_Sync,
              Direction)

        CUT_CONFIG3 = np.dtype(
            {'names': ['Ground_Clutter_Classifier_Type', 'Ground_Clutter_Filter_Type',
                       'Ground_Clutter_Filter_Notch_Width',
                       'Ground_Clutter_Filter_Window', "reserve"],
             'formats': ['h', 'h', 'h', 'h', 'S72']})
        [Ground_Clutter_Classifier_Type, Ground_Clutter_Filter_Type, Ground_Clutter_Filter_Notch_Width,
         Ground_Clutter_Filter_Window, _] = \
            np.fromfile(file=self.fi, dtype=CUT_CONFIG3, count=1, sep='')[0]
        print(Ground_Clutter_Classifier_Type, Ground_Clutter_Filter_Type, Ground_Clutter_Filter_Notch_Width,
              Ground_Clutter_Filter_Window)

    def parse_MOMENT_DATA(self, eleNum):

        rData = []
        vData = []
        sData = []
        tData = []
        SQIData = []
        ZDRData = []
        CCData = []
        DPData = []
        KDPData = []
        SNRHData = []
        azimuthR = []
        azimuthV = []
        elevationR = []
        elevationV = []
        numGatesR = 0
        numGatesV = 0
        numRadialsR = 0
        numRadialsV = 0
        timeR = []
        timeV = []

        # /**
        #   * 径向数据状态
        #   * 0–仰角开始
        #   * 1–中间数据
        #   * 2–仰角结束
        #   * 3–体扫开始
        #   * 4–体扫结束
        #   * 5–RHI开始
        #   * 6–RHI结束
        #   */
        isFinished = 0
        Length_of_data_all = 0

        while not (isFinished == 2 or isFinished == 4):

            MOMENT_DATA_BLOCK_HEAD = np.dtype(
                {'names': ['Radial_State', 'Spot_Blank', 'Sequence_Number', 'Radial_Number', 'Elevation_Number',
                           'Azimuth',
                           'Elevation', 'Seconds', 'Microseconds', 'Length_of_data', 'Moment_Number', "reserve"],
                 'formats': ['i', 'i', 'i', 'i', 'i', 'f', 'f', 'i', 'i', 'i', 'i', 'S20']})
            [Radial_State, Spot_Blank, Sequence_Number, Radial_Number, Elevation_Number, Azimuth, Elevation, Seconds,
             Microseconds
                , Length_of_data, Moment_Number, _] = \
                np.fromfile(file=self.fi, dtype=MOMENT_DATA_BLOCK_HEAD, count=1, sep='')[0]
            isFinished = Radial_State
            # print("径向数据块头 Radial_State:", Radial_State, "Spot_Blank:", Spot_Blank, "Sequence_Number:", Sequence_Number,
            #       "Radial_Number:", Radial_Number, "Elevation_Number:", Elevation_Number, "Azimuth3:", Azimuth,
            #       "Elevation:", Elevation, "Seconds:", Seconds, "Microseconds:", Microseconds, "Length_of_data:",
            #       Length_of_data, "Moment_Number:", Moment_Number)

            if Elevation_Number != eleNum:
                print("something wrong")
                return None

            azimuthR.append(Azimuth)
            azimuthV.append(Azimuth)

            elevationR.append(Elevation)
            elevationV.append(Elevation)

            timeR.append(Seconds)
            timeV.append(Seconds)

            for i in range(Moment_Number):
                MOMENT_DATA_HEAD = np.dtype(
                    {'names': ['Data_Type', 'Scale', 'Offset', 'Bin_Length', 'Flags', 'Length', 'reserve'],
                     'formats': ['i', 'i', 'i', 'h', 'h', 'i', 'S12']})
                [Data_Type, Scale, Offset, Bin_Length, Flags, Length, _] = \
                    np.fromfile(file=self.fi, dtype=MOMENT_DATA_HEAD, count=1, sep='')[0]

                # print("   径向数据头 Data_Type:", Data_Type, "Scale:", Scale, "Offset:", Offset, "Bin_Length:", Bin_Length, "Flags:",
                #       Flags, "Length:", Length)

                dtypeType = None
                if Bin_Length == 1:
                    dtypeType = np.uint8
                else:
                    dtypeType = np.uint16
                data = np.fromfile(file=self.fi, dtype=dtypeType, count=Length // Bin_Length)
                data = data.astype(np.float32)
                data[data < 5] = np.nan
                data = list((data - Offset) / Scale)

                # //添加数据块
                if Data_Type == 2:
                    rData.append(data)
                    numGatesR = Length / Bin_Length
                    numRadialsR = Radial_Number
                # print("lengthR:", numGatesR, numGatesV)

                elif (Data_Type == 3):
                    vData.append(data)
                    numGatesV = Length / Bin_Length
                    numRadialsV = Radial_Number
                # print("lengthV:", numGatesR, numGatesV)

                elif (Data_Type == 4):
                    sData.append(data)

                elif (Data_Type == 1):
                    tData.append(data)
                elif (Data_Type == 5):
                    SQIData.append(data)
                elif (Data_Type == 7) :
                    ZDRData.append(data)
                elif (Data_Type == 9) :
                    CCData.append(data)
                elif (Data_Type == 10) :
                    DPData.append(data)
                elif (Data_Type == 11) :
                    KDPData.append(data)
                elif (Data_Type == 16):
                    SNRHData.append(data)


        return {"Length_of_data_all": Length_of_data_all, "azimuthR": azimuthR, "azimuthV": azimuthV,
                "elevationR": elevationR, "elevationV": elevationV, "numGatesR": numGatesR, "numGatesV": numGatesV,
                "numRadialsR": numRadialsR, "numRadialsV": numRadialsV, "timeR": timeR, "timeV": timeV,
                "RadialVelocity": vData, "Reflectivity": rData, "SpectrumWidth": sData, "TotalReflectivity": tData,
                "SignalQualityIndex": SQIData, "DifferentialReflectivity": ZDRData,
                "CrossCorrelationCoefficient": CCData, "DifferentialPhase": DPData,
                "SpecificDifferentialPhase": KDPData, "HorizontalSignalNoiseRatio": SNRHData}

    def mkNC(self, outpath, rC):
        os.makedirs(os.path.dirname(outpath), exist_ok=True)
        a = nc.Dataset(outpath, "w", format='NETCDF4')
        a.createDimension("scanR", len(rC["elevationR"]))
        a.createDimension("scanV", len(rC["elevationV"]))
        radialMax = max(np.max(rC["numRadialsR"]), np.max(rC["numRadialsV"]))

        # println(radialMax)
        a.createDimension("radial", radialMax)
        a.createDimension("gateR", len(rC["distanceR"]))
        a.createDimension("gateV", len(rC["distanceV"]))

        a.createVariable("azimuthR", "f", ["scanR", "radial"])
        a.createVariable("azimuthV", "f", ["scanV", "radial"])
        a.createVariable("distanceR", "f", ["gateR"])
        a.createVariable("distanceV", "f", ["gateV"])
        a.createVariable("elevationR", "f", ["scanR", "radial"])
        a.createVariable("elevationV", "f", ["scanV", "radial"])
        a.createVariable("numGatesR", "i", ["scanR"])
        a.createVariable("numGatesV", "i", ["scanV"])
        a.createVariable("numRadialsR", "i", ["scanR"])
        a.createVariable("numRadialsV", "i", ["scanV"])
        tR = a.createVariable("timeR", "i", ["scanR", "radial"])
        tR.missing_value = -1
        tV = a.createVariable("timeV", "i", ["scanV", "radial"])
        tV.missing_value = -1
        v = a.createVariable("RadialVelocity", "f", ["scanV", "radial", "gateV"], zlib=True)
        v.valid_range = [-62, 62]
        a.createVariable("SpectrumWidth", "f", ["scanV", "radial", "gateV"], zlib=True)
        a.createVariable("Reflectivity", "f", ["scanR", "radial", "gateR"], zlib=True)
        if self.isDual:
            a.createVariable("TotalReflectivity", "f", ["scanR", "radial", "gateR"], zlib=True)
            a.createVariable("SignalQualityIndex", "f", ["radial", "gateR"], zlib=True)
            a.createVariable("DifferentialReflectivity", "f", ["scanR", "radial", "gateR"], zlib=True)
            a.createVariable("CrossCorrelationCoefficient", "f", ["scanR", "radial", "gateR"], zlib=True)
            a.createVariable("DifferentialPhase", "f", ["scanR", "radial", "gateR"], zlib=True)
            a.createVariable("SpecificDifferentialPhase", "f4", ["scanR", "radial", "gateR"], zlib=True)
            a.createVariable("HorizontalSignalNoiseRatio", "f4", ["scanR", "radial", "gateR"], zlib=True)

        # print(len(rC["azimuthR"]), len(rC["azimuthR"][0]))
        # print(rC["azimuthR"])
        # print(a.variables["azimuthR"][:].shape)
        # print(rC["azimuthR"].shape)
        a.variables["azimuthR"][:] = rC["azimuthR"]
        a.variables["azimuthV"][:] = rC["azimuthV"]
        a.variables["distanceR"][:] = rC["distanceR"]
        a.variables["distanceV"][:] = rC["distanceV"]
        a.variables["elevationR"][:] = rC["elevationR"]
        a.variables["elevationV"][:] = rC["elevationV"]
        a.variables["numGatesR"][:] = rC["numGatesR"]
        a.variables["numGatesV"][:] = rC["numGatesV"]
        a.variables["numRadialsR"][:] = rC["numRadialsR"]
        a.variables["numRadialsV"][:] = rC["numRadialsV"]
        a.variables["timeR"][:] = rC["timeR"]
        a.variables["timeV"][:] = rC["timeV"]
        a.variables["RadialVelocity"][:] = rC["RadialVelocity"]
        a.variables["SpectrumWidth"][:] = rC["SpectrumWidth"]
        a.variables["Reflectivity"][:] = rC["Reflectivity"]
        if self.isDual:
            a.variables["TotalReflectivity"][:]=rC["TotalReflectivity"]
            a.variables["SignalQualityIndex"][:]=rC["SignalQualityIndex"]
            a.variables["DifferentialReflectivity"][:]=rC["DifferentialReflectivity"]
            a.variables["CrossCorrelationCoefficient"][:]=rC["CrossCorrelationCoefficient"]
            a.variables["DifferentialPhase"][:]=rC["DifferentialPhase"]
            a.variables["SpecificDifferentialPhase"][:]=rC["SpecificDifferentialPhase"]
            a.variables["HorizontalSignalNoiseRatio"][:]=rC["HorizontalSignalNoiseRatio"]

        a.close()

        return None

    def main(self,outparent):
        self.parse_GENERIC_HEADER()
        self.parse_SITE_CONFIG()
        self.parse_TASK_CONFIG()
        for i in range(self.Cut_Number):
            self.parse_read_CUT_CONFIG()

        rData = []
        vData = []
        sData = []
        azimuthR = []
        azimuthV = []
        tData = []
        SQIData = []
        SQIData2D = []
        ZDRData = []
        CCData = []
        DPData = []
        KDPData = []
        SNRHData = []
        distanceR = []
        distanceV = []
        elevationR = []
        elevationV = []
        numGatesR = []
        numGatesV = []
        numRadialsR = []
        numRadialsV = []
        timeR = []
        timeV = []

        for i in range(self.Cut_Number):
            a = self.parse_MOMENT_DATA(i + 1)

            if len(a["Reflectivity"]) != 0:
                azimuthR.append(a["azimuthR"])
                elevationR.append(a["elevationR"])

                # // println(a.Reflectivity.length)
                # // println(s"a.numGatesR:${a.numGatesR}")
                numGatesR.append(a["numGatesR"])
                numRadialsR.append(a["numRadialsR"])
                timeR.append(a["timeR"])
                rData.append(a["Reflectivity"])

            if len(a["RadialVelocity"]) != 0:
                azimuthV.append(a["azimuthV"])
                elevationV.append(a["elevationV"])
                numGatesV.append(a["numGatesV"])
                numRadialsV.append(a["numRadialsV"])
                timeV.append(a["timeV"])
                vData.append(a["RadialVelocity"])
                sData.append(a["SpectrumWidth"])

            if len(a["SignalQualityIndex"]) != 0:
                SQIData.append(a["SignalQualityIndex"])
            if len(a["TotalReflectivity"]) != 0:
                tData.append(a["TotalReflectivity"])
                ZDRData.append(a["DifferentialReflectivity"])
                CCData.append(a["CrossCorrelationCoefficient"])
                DPData.append(a["DifferentialPhase"])
                KDPData.append(a["SpecificDifferentialPhase"])
                SNRHData.append(a["HorizontalSignalNoiseRatio"])



        if (len(azimuthR) == 11):
            azimuthR = azimuthR[0:1] + azimuthR[2:3] + azimuthR[4:11]
            elevationR = elevationR[0:1] + elevationR[2:3] + elevationR[4:11]
            numGatesR = numGatesR[0:1] + numGatesR[2:3] + numGatesR[4:11]
            numRadialsR = numRadialsR[0:1] + numRadialsR[2:3] + numRadialsR[4:11]
            timeR = timeR[0:1] + timeR[2:3] + timeR[4:11]
            rData = rData[0:1] + rData[2:3] + rData[4:11]
            azimuthV = azimuthV[1:2] + azimuthV[3:11]
            elevationV = elevationV[1:2] + elevationV[3:11]
            numGatesV = numGatesV[1:2] + numGatesV[3:11]
            numRadialsV = numRadialsV[1:2] + numRadialsV[3:11]
            timeV = timeV[1:2] + timeV[3:11]
            vData = vData[1:2] + vData[3:11]
            sData = sData[1:2] + sData[3:11]

        # 选取最大的库数
        print(numGatesR)
        distanceR = list(map(lambda x: x * self.Log_Resolution, range(int(np.max(numGatesR)))))
        distanceV = list(map(lambda x: x * self.Doppler_Resolution, range(int(np.max(numGatesV)))))

        print(numRadialsR, numRadialsV)
        radialMax = max(np.max(np.asarray(numRadialsR)), np.max(np.asarray(numRadialsV)))
        gateRMax = int(np.max(np.asarray(numGatesR)))
        gateVMax = int(np.max(np.asarray(numGatesV)))
        print(gateRMax, gateVMax)
        azimuthR = pad2D(azimuthR, radialMax)
        azimuthV = pad2D(azimuthV, radialMax)
        elevationR = pad2D(elevationR, radialMax)
        elevationV = pad2D(elevationV, radialMax)
        timeR = pad2D(timeR, radialMax)
        timeV = pad2D(timeV, radialMax)
        tData = pad3D(tData, radialMax, gateRMax)
        vData = pad3D(vData, radialMax, gateVMax)
        sData = pad3D(sData, radialMax, gateVMax)
        rData = pad3D(rData, radialMax, gateRMax)

        # print(SQIData)
        if self.isDual:
            SQIData2D = pad3D([SQIData[0]], radialMax, gateRMax)
            ZDRData = pad3D(ZDRData, radialMax, gateRMax)
            CCData = pad3D(CCData, radialMax, gateRMax)
            DPData = pad3D(DPData, radialMax, gateRMax)
            KDPData = pad3D(KDPData, radialMax, gateRMax)
            SNRHData = pad3D(SNRHData, radialMax, gateRMax)
        print(rData.shape)




        b = {"azimuthR": azimuthR, "azimuthV": azimuthV, "distanceR": distanceR, "distanceV": distanceV,
             "elevationR": elevationR, "elevationV": elevationV, "numGatesR": numGatesR, "numGatesV": numGatesV,
             "numRadialsR": numRadialsR, "numRadialsV": numRadialsV, "timeR": timeR, "timeV": timeV,
             "RadialVelocity": vData,
             "Reflectivity": rData, "SpectrumWidth": sData, "TotalReflectivity": tData,
             "SignalQualityIndex": SQIData2D, "DifferentialReflectivity": ZDRData,
             "CrossCorrelationCoefficient": CCData,
             "DifferentialPhase": DPData, "SpecificDifferentialPhase": KDPData, "HorizontalSignalNoiseRatio": SNRHData}
        timtStr=self.datetime.strftime("%Y%m%d%H%M%S")
        outputPath="%s/%s/%s/%s/Z_RADR_I_%s_%s_O_DOR_%s_CAP_FMT.nc"%(outparent,timtStr[:4],timtStr[:8],self.radarID,self.radarID,timtStr,self.type)
        os.makedirs(os.path.dirname(outputPath),exist_ok=True)
        self.mkNC(outputPath, b)
        self.fi.close()
        os.remove(self.path)

if __name__ == "__main__":

    outputFile = "Z_RADR_I_Z9891_20200909000044_O_DOR_CD_CAP_FMT.bin.bz2"
    a = readCinrad(outputFile)
    a.main("./radarNC")

