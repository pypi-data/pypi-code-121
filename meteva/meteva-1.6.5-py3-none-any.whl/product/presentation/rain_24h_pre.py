import datetime
import meteva

para_example= {
    "day_num":30,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "defalut_value":0,
    "hdf_file_name":"week.h5",
    "interp": meteva.base.interp_gs_nearest,
    "ob_data":{
        "hdf_dir":r"O:\data\sta\SURFACE\RAIN24_NATIONAL",
        "dir_ob": r"O:\data\sta\SURFACE\RAIN24_NATIONAL_HH-HH\YYYYMMDD\YYYYMMDDHH0000.000",
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {"element_id":1011},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "ECMWF":{
            "hdf_dir": r"O:\data\grid\ECMWF_HR\rain24",
            "dir_fo": r"O:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.diag.change_dtime,
            "operation_para": {"dtime": 24}
        },
    },
    "output_dir":r"O:\data\hdf\combined\rain24"
}


if __name__ == '__main__':
    file = r"O:\data\sta\SURFACE\RAIN24_NATIONAL_08-08\20200812\20200812080000.000"
    #meteva.base.io.print_gds_file_values_names(file)
    #meteva.base.print_gds_file_values_names(filename)
    meteva.product.prepare_dataset(para_example)