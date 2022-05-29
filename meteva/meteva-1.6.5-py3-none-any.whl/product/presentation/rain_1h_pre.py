import datetime
import meteva

para_example= {
    "day_num":5,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "defalut_value":0,
    "hdf_file_name":"week.h5",
    "interp": meteva.base.interp_gs_nearest,
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "GMOSRR":{
            "hdf_dir": r"O:\data\grid\GMOSRR\ROLLING_UPDATE\RAIN01",
            "dir_fo": r"O:\data\grid\GMOSRR\ROLLING_UPDATE\RAIN01\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },
    },
    "output_dir":r"O:\data\hdf\combined\rain01"
}


if __name__ == '__main__':
    meteva.product.prepare_dataset(para_example)