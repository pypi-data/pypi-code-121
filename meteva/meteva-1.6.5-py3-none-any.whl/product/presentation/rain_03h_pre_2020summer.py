import datetime
import meteva

para_example= {
    "day_num":200,
    "end_time":datetime.datetime.now(),
    "station_file":r"H:\task\other\202009-veri_objective_method\sta_info.m3",
    "defalut_value":0,
    "hdf_file_name":"summer_3h.h5",
    "interp": meteva.base.interp_gs_nearest,
    "ob_data":{
        "hdf_dir":r"H:\task\other\202009-veri_objective_method\ob_rain03",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "hour":None,
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {"element_id":1003},
        "reasonable_value": [0, 1000],
        "operation":meteva.base.fun.sum_of_sta,
        "operation_para": {"used_coords":["time"],"span":3},
        "time_type": "BT",
    },
    "fo_data":{
        "ECMWF": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\ECMWF_HR\rain03",
            "dir_fo": r"O:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour":[8,20,12],
            "dtime":[0,84,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.change,
            "operation_para": {"used_coords": "dtime", "delta": 3},
            "time_type": "BT",
            "move_fo_time": 12
        },
        "GRAPES_meso": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Grapes_meso\rain03",
            "dir_fo": r"O:\data\grid\GRAPES_MESO_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[0, 84,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.change,
            "operation_para": {"used_coords": "dtime", "delta": 3},
            "time_type": "BT",
            "move_fo_time": 12
        },
        "Forecaster": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Forecaster\rain03",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\RAIN03\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[3, 84,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": None,
            "time_type": "BT",
            "move_fo_time": 0
        },
        "Province": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Province\rain03",
            "dir_fo": r"O:\data\grid\NWFD_SMERGE\RAIN03\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[3, 84,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":  None,
            "time_type":"BT",
            "move_fo_time": 0
        },
        "Objective_method": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\ObjectiveMethod\rain03",
            "dir_fo": r"\\10.20.90.107\sm_qpf\combine_03h\sfc\YYYYMMDDHH\YYYYMMDDHH.TTT.m4.m4",
            "hour": [8, 20, 12],
            "dtime": [3, 84, 3],
            "read_method": meteva.base.io.read_griddata_from_micaps4,
            "read_para": {},
            "operation": None,
            "operation_para": None,
            "time_type":"UT",
            "move_fo_time": 12,
        },
    },
    "output_dir":r"H:\task\other\202009-veri_objective_method"
}


if __name__ == '__main__':
    import meteva.base as meb
    import meteva.product as mpd
    import meteva.method as mem
    import pandas as pd
    file = r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION\20200909\20200909000000.000"
    meteva.product.prepare_dataset(para_example)
    hdf_file = r"H:\task\other\202009-veri_objective_method/summer_3h.h5"
    sta_all = pd.read_hdf(hdf_file)
    sta_all = meb.sele.not_IV(sta_all)
    print(sta_all)
    mpd.score(sta_all,mem.bias,grade_list= [0.1,5,10,20,40],g = "dtime",plot = "bar",dpi = 100,save_path=r"H:\task\other\202009-veri_objective_method/bias.png")