import datetime
import meteva
import pandas as pd

para_example= {
    "begin_time":datetime.datetime(2020,6,23,17,0),
    "end_time":datetime.datetime(2020,7,13,8,0),
    "station_file":r"E:\QPE_data\ob\station_shuiwen.txt",
    "defalut_value":0,
    "interp": meteva.base.interp_gs_nearest,
    "hdf_file_name":"summer_shuiwen_1km.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "hour": None,
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {},
        "reasonable_value": [0, 1000],
        "operation":None,
        "operation_para":{},
        "time_type": "BT",
    },
    "fo_data":{
        "NMIC_TRI": {
            "hdf_dir": r"O:\data\hdf\qpe\nmic_tri",
            "dir_fo": r"E:\QPE_data\qpe_nmic\01h\nmic_1km\YYMMDDHH.TTT",
            "hour": [0, 24,1],
            "dtime": [0,0,1],
            "read_method": meteva.base.io.read_griddata_from_micaps4,
            "read_para": {},
            "operation": None,
            "operation_para": {},
            "move_fo_time": 0,
            "time_type": "BT",
        },
        "NMC": {
            "hdf_dir": r"O:\data\hdf\qpe\nmc",
            "dir_fo": r"E:\QPE_data\result\qpe\qpe_ob_nosplit\n10\d2\YYYY\YYMMDDHH.000.nc",
            "hour": [0, 24, 1],
            "dtime": [0, 0,1],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": {},
            "move_fo_time": 0,
            "time_type": "BT",
        },

    },
    "output_dir":r"O:\data\hdf\qpe"
}


if __name__ == '__main__':
    meteva.product.prepare_dataset(para_example)