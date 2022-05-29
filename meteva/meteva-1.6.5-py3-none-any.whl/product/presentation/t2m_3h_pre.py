import datetime
import meteva

para_example= {
    "begin_time":datetime.datetime.now() - datetime.timedelta(days=30),
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "defalut_value":999999,
    "interp": meteva.base.interp_gs_linear,
    "hdf_file_name":"week.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\TMP_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\TMP_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "hour": None,
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {},
        "reasonable_value": [-100, 100],
        "operation":None,
        "operation_para":{},
        "time_type": "BT",
    },
    "fo_data":{
        "SCMOC":{
            "hdf_dir": r"O:\data\hdf\NWFD_SCMOC\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20, 12],
            "dtime": [0, 240, 3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":{},
            "move_fo_time": 0,
            "time_type": "BT",
            "reasonable_value": [-100, 100],
        },
        "GRAPES": {
            "hdf_dir": r"O:\data\hdf\GRAPES_GFS\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\GRAPES_GFS\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20, 12],
            "dtime": [0, 240, 3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": {},
            "move_fo_time": 12,
            "time_type": "BT",
            "reasonable_value": [-100, 100],
        },
        "ECMWF":{
            "hdf_dir": r"O:\data\hdf\ECMWF_HR\TMP_2M",
            "dir_fo": r"O:\data\grid\ECMWF_HR\TMP_2M\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20, 12],
            "dtime": [0, 240, 3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":{},
            "move_fo_time": 12,
            "time_type": "BT",
            "reasonable_value": [-100, 100],
        }
    },
    "output_dir":r"O:\data\hdf\combined\temp_2m"
}


if __name__ == '__main__':
    meteva.product.prepare_dataset(para_example)