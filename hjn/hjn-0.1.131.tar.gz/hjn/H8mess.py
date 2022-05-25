import numpy as np
from hjn.mkNCHJN import envelope
import datetime

class parseHimawari():
    def __init__(self):
        self.res = 12100000
        self.nlin = 1100
        self.ncol = 11000
        self.data=None

    def read_Himawari(self,inputfile):
        resolution=int(inputfile[-12:-10])
        if resolution==10:
            self.res=12100000
            self.nlin=1100
            self.ncol=11000
        elif resolution==20:
            self.res=3025000
            self.nlin=550
            self.ncol=5500
        elif resolution == 5:
            self.res=48400000
            self.nlin=2200
            self.ncol=22000
        band=int(inputfile[-21:-19])
        if band < 7:
            formation = [('Block number1', 'i1', 1), \
                         ('Block length1', 'i2', 1), \
                         ('Total number of header blocks ', 'i2', 1), \
                         ('Byte order', 'i1', 1), \
                         ('Satellite name', 'S1', 16), \
                         ('Processing center name', 'S1', 16), \
                         ('Observation area', 'S1', 4), \
                         ('Other observation information', 'S1', 2), \
                         ('Observation timeline', 'i2', 1), \
                         ('Observation start time', 'float64', 1), \
                         ('Observation end time', 'float64', 1), \
                         ('File creation time', 'float64', 1), \
                         ('Total header length', 'i4', 1), \
                         ('Total data length', 'i4', 1), \
                         ('Quality flag 1', 'i1', 1), \
                         ('Quality flag 2 ', 'i1', 1), \
                         ('Quality flag 3', 'i1', 1), \
                         ('Quality flag 4', 'i1', 1), \
                         ('File format version', 'S1', 32), \
                         ('File name ', 'S1', 128), \
                         ('Spare1', 'S1', 40), \

                         ('Block number2', 'i1', 1), \
                         ('Block length2', 'i2', 1), \
                         ('Number of bits per pixel', 'i2', 1), \
                         ('Number of columns', 'i2', 1), \
                         ('Number of lines', 'i2', 1), \
                         ('Compression flag for data', 'i1', 1), \
                         ('Spare2', 'S1', 40), \

                         ('Block number3', 'i1', 1), \
                         ('Block length3', 'i2', 1), \
                         ('sub_lon', 'float64', 1), \
                         ('Column scaling factor', 'i4', 1), \
                         ('Line scaling factor', 'i4', 1), \
                         ('Column offset', 'float32', 1), \
                         ('Line offset', 'float32', 1), \
                         ('Distance from Earth’s center to virtual satellite', 'float64', 1), \
                         ('Earth’s equatorial radius', 'float64', 1), \
                         ('Earth’s polar radius', 'float64', 1), \
                         ('var1', 'float64', 1), \
                         ('var2', 'float64', 1), \
                         ('var3', 'float64', 1), \
                         ('Coefficient for sd', 'float64', 1), \
                         ('Resampling types', 'i2', 1), \
                         ('Resampling size', 'i2', 1), \
                         ('Spare3', 'S1', 40), \

                         ('Block number4', 'i1', 1), \
                         ('Block length4', 'i2', 1), \
                         ('Navigation information time', 'float64', 1), \
                         ('SSP longitude', 'float64', 1), \
                         ('SSP latitude', 'float64', 1), \
                         ('Distance from Earth’s center to Satellite', 'float64', 1), \
                         ('Nadir longitude', 'float64', 1), \
                         ('Nadir latitude', 'float64', 1), \
                         ('Sun’s position', 'float64', 3), \
                         ('Moon’s position', 'float64', 3), \
                         ('Spare4', 'S1', 40), \

                         ('Block number5', 'i1', 1), \
                         ('Block length5', 'i2', 1), \
                         ('Band number', 'i2', 1), \
                         ('Central wave length', 'float64', 1), \
                         ('Valid number of bits per pixel', 'i2', 1), \
                         ('Count value of error pixels', 'uint16', 1), \
                         ('Count value of pixels outside scan area', 'uint16', 1), \
                         ('Slope for count-radiance conversion equation', 'float64', 1), \
                         ('Intercept for count-radiance conversion equation', 'float64', 1), \
                         ('Coefficient for transformation from radiance  to albedo', 'float64', 1), \
                         ('Update time of the values of the following No. 12 and No. 13', 'float64', 1), \
                         ('Calibrated Slope for count-radiance conversion equation_updated value of No. 8 of this block ', 'float64', 1),\
                         ('Calibrated Intercept for count-radiance conversion equation_updated value of No. 9 of this block ', 'float64', 1),\
                         ('Spare5', 'S1', 80), \

                         ('Block number6', 'i1', 1), \
                         ('Block length6', 'i2', 1), \
                         ('GSICS calibration coefficient_Intercept', 'float64', 1), \
                         ('GSICS calibration coefficient_Slope', 'float64', 1), \
                         ('GSICS calibration coefficient_Quadratic term', 'float64', 1), \
                         ('Radiance bias for standard scene', 'float64', 1), \
                         ('Uncertainty of radiance bias for standard scene', 'float64', 1), \
                         ('Radiance for standard scene', 'float64', 1), \
                         ('Start time of GSICS Correction validity period', 'float64', 1), \
                         ('End time of GSICS Correction validity period', 'float64', 1), \
                         ('Radiance validity range of GSICS calibration coefficients_upper limit', 'float32', 1), \
                         ('Radiance validity range of GSICS calibration coefficients_lower limit', 'float32', 1), \
                         ('File name of GSICS Correction', 'S1', 128), \
                         ('Spare6', 'S1', 56), \

                         ('Block number7', 'i1', 1), \
                         ('Block length7', 'i2', 1), \
                         ('Total number of segments', 'i1', 1), \
                         ('Segment sequence number', 'i1', 1), \
                         ('First line number of image segment', 'i2', 1), \
                         ('Spare7', 'S1', 40), \

                         ('Block number8', 'i1', 1), \
                         ('Block length8', 'i2', 1), \
                         ('Center column of rotation', 'float32', 1), \
                         ('Center line of rotation', 'float32', 1), \
                         ('Amount of rotational correction', 'float64', 1), \
                         ('Number of correction information data for column and line direction', 'i2', 1), \
                         ('Line number after rotation', 'i2', 1), \
                         ('Shift amount for column direction', 'float32', 1), \
                         ('Shift amount for line direction8', 'float32', 1), \
                         ('Spare8', 'S1', 50), \

                         ('Block number9', 'i1', 1), \
                         ('Block length9', 'i2', 1), \
                         ('Number of observation times9', 'i2', 1), \
                         ('Line number9', 'i2', 1), \
                         ('Observation time9', 'float64', 1), \
                         ('Spare9', 'S1', 70), \

                         ('Block number10', 'i1', 1), \
                         ('Block length10', 'i4', 1), \
                         ('Number of error information data', 'i2', 1), \
                         ('Line number10', 'i2', 1), \
                         ('Number of error pixels per line10', 'i2', 1), \
                         ('Spare10', 'S1', 36), \

                         ('Block number11', 'i1', 1), \
                         ('Block length11', 'i2', 1), \
                         ('Spare11', 'S1', 256), \

                         ('Count value of each pixel', 'i2', self.res)]
        else:
            formation=[('Block number1','i1',1),\
                        ('Block length1','i2',1),\
                        ('Total number of header blocks ','i2',1),\
                        ('Byte order','i1',1),\
                        ('Satellite name','S1',16),\
                        ('Processing center name','S1',16),\
                        ('Observation area','S1',4),\
                        ('Other observation information','S1',2),\
                        ('Observation timeline','i2',1),\
                        ('Observation start time','float64',1),\
                        ('Observation end time','float64',1),\
                        ('File creation time','float64',1),\
                        ('Total header length','i4',1),\
                        ('Total data length','i4',1),\
                        ('Quality flag 1','i1',1),\
                        ('Quality flag 2 ','i1',1),\
                        ('Quality flag 3','i1',1),\
                        ('Quality flag 4','i1',1),\
                        ('File format version','S1',32),\
                        ('File name ','S1',128),\
                        ('Spare1','S1',40),\

                        ('Block number2','i1',1),\
                        ('Block length2','i2',1),\
                        ('Number of bits per pixel','i2',1),\
                        ('Number of columns','i2',1),\
                        ('Number of lines','i2',1),\
                        ('Compression flag for data','i1',1),\
                        ('Spare2','S1',40),\

                        ('Block number3','i1',1),\
                        ('Block length3','i2',1),\
                        ('sub_lon','float64',1),\
                        ('Column scaling factor','i4',1),\
                        ('Line scaling factor','i4',1),\
                        ('Column offset','float32',1),\
                        ('Line offset','float32',1),\
                        ('Distance from Earth’s center to virtual satellite','float64',1),\
                        ('Earth’s equatorial radius','float64',1),\
                        ('Earth’s polar radius','float64',1),\
                        ('var1','float64',1),\
                        ('var2','float64',1),\
                        ('var3','float64',1),\
                        ('Coefficient for sd','float64',1),\
                        ('Resampling types','i2',1),\
                        ('Resampling size','i2',1),\
                        ('Spare3','S1',40),\

                        ('Block number4','i1',1),\
                        ('Block length4','i2',1),\
                        ('Navigation information time','float64',1),\
                        ('SSP longitude','float64',1),\
                        ('SSP latitude','float64',1),\
                        ('Distance from Earth’s center to Satellite','float64',1),\
                        ('Nadir longitude','float64',1),\
                        ('Nadir latitude','float64',1),\
                        ('Sun’s position','float64',3),\
                        ('Moon’s position','float64',3),\
                        ('Spare4','S1',40),\

                        ('Block number5','i1',1),\
                        ('Block length5','i2',1),\
                        ('Band number','i2',1),\
                        ('Central wave length','float64',1),\
                        ('Valid number of bits per pixel','i2',1),\
                        ('Count value of error pixels','i2',1),\
                        ('Count value of pixels outside scan area','i2',1),\
                        ('Slope for count-radiance conversion equation','float64',1),\
                        ('Intercept for count-radiance conversion equation','float64',1),\
                        ('radiance to brightness temperature_c0','float64',1),\
                        ('radiance to brightness temperature_c1','float64',1),\
                        ('radiance to brightness temperature_c2','float64',1),\
                        ('brightness temperature to radiance_C0','float64',1),\
                        ('brightness temperature to radianceC1','float64',1),\
                        ('brightness temperature to radianceC2','float64',1),\
                        ('Speed of light','float64',1),\
                        ('Planck constant','float64',1),\
                        ('Boltzmann constant','float64',1),\
                        ('Spare5','S1',40), \

                       ('Block number6', 'i1', 1), \
                       ('Block length6', 'i2', 1), \
                       ('GSICS calibration coefficient_Intercept', 'float64', 1), \
                       ('GSICS calibration coefficient_Slope', 'float64', 1), \
                       ('GSICS calibration coefficient_Quadratic term', 'float64', 1), \
                       ('Radiance bias for standard scene', 'float64', 1), \
                       ('Uncertainty of radiance bias for standard scene', 'float64', 1), \
                       ('Radiance for standard scene', 'float64', 1), \
                       ('Start time of GSICS Correction validity period', 'float64', 1), \
                       ('End time of GSICS Correction validity period', 'float64', 1), \
                       ('Radiance validity range of GSICS calibration coefficients_upper limit', 'float32', 1), \
                       ('Radiance validity range of GSICS calibration coefficients_lower limit', 'float32', 1), \
                       ('File name of GSICS Correction', 'S1', 128), \
                       ('Spare6', 'S1', 56), \

                       ('Block number7', 'i1', 1), \
                       ('Block length7', 'i2', 1), \
                       ('Total number of segments', 'i1', 1), \
                       ('Segment sequence number', 'i1', 1), \
                       ('First line number of image segment', 'i2', 1), \
                       ('Spare7', 'S1', 40), \

                       ('Block number8', 'i1', 1), \
                       ('Block length8', 'i2', 1), \
                       ('Center column of rotation', 'float32', 1), \
                       ('Center line of rotation', 'float32', 1), \
                       ('Amount of rotational correction', 'float64', 1), \
                       ('Number of correction information data for column and line direction', 'i2', 1), \
                       ('Line number after rotation', 'i2', 1), \
                       ('Shift amount for column direction', 'float32', 1), \
                       ('Shift amount for line direction8', 'float32', 1), \
                       ('Spare8', 'S1', 50), \

                       ('Block number9', 'i1', 1), \
                       ('Block length9', 'i2', 1), \
                       ('Number of observation times9', 'i2', 1), \
                       ('Line number9', 'i2', 1), \
                       ('Observation time9', 'float64', 1), \
                       ('Spare9', 'S1', 70), \

                       ('Block number10', 'i1', 1), \
                       ('Block length10', 'i4', 1), \
                       ('Number of error information data', 'i2', 1), \
                       ('Line number10', 'i2', 1), \
                       ('Number of error pixels per line10', 'i2', 1), \
                       ('Spare10', 'S1', 36), \

                       ('Block number11', 'i1', 1), \
                       ('Block length11', 'i2', 1), \
                       ('Spare11', 'S1', 256), \


                       ('Count value of each pixel', 'i2', self.res)]

        self.data=np.fromfile(inputfile,dtype=formation)[0]
        band=int(inputfile[-21:-19])

        mat = self.data["Count value of each pixel"].reshape([self.nlin, self.ncol])
        mat=self.toRealVal(mat,band)
        return mat

    def toRealVal(self,mat,bandNo):
        radiance1=mat * self.data["Slope for count-radiance conversion equation"] + self.data["Intercept for count-radiance conversion equation"]

        radiance2 = radiance1*self.data["Coefficient for transformation from radiance  to albedo"] if bandNo >= 1 and bandNo <= 6 else self.hisd_radiance_to_tbb(radiance1)

        return radiance2

    def hisd_radiance_to_tbb(self, radiance0):
        lmbd = self.data['Central wave length'] / 1000000.0
        radiance = radiance0 * 1000000.0
        planck_c1 = 2.0 * self.data['Planck constant'] * self.data['Speed of light']**2.0 / lmbd**5.0
        planck_c2 = self.data['Planck constant'] * self.data['Speed of light'] / (self.data['Boltzmann constant'] * lmbd)
        effective_temperature = planck_c2 / np.log((planck_c1 / radiance) + 1.0)
        tbb = self.data['radiance to brightness temperature_c0'] + self.data['radiance to brightness temperature_c1'] * effective_temperature + self.data['radiance to brightness temperature_c2'] * effective_temperature**2
        tbb[radiance<0]=np.nan
        return tbb

if __name__=="__main__":
    h8P=parseHimawari()
    data = h8P.read_Himawari("")

