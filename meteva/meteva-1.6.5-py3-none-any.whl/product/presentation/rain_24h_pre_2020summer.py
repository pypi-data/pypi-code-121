import datetime
import meteva

para_example= {
    "begin_time":datetime.datetime(2020,5,1,8,0),
    "end_time":datetime.datetime(2020,9,20,20,0),
    "station_file":r"H:\task\other\202009-veri_objective_method\sta_info.m3",
    "defalut_value":0,
    "hdf_file_name":"summer.h5",
    "interp": meteva.base.interp_gs_nearest,
    "ob_data":{
        "hdf_dir":r"H:\task\other\202009-veri_objective_method\ob_rain24",
        "dir_ob": r"Z:\data\surface\jiany_rr\r20\YYMMDDHH.000",
        "hour":None,
        "read_method": meteva.base.io.read_stadata_from_micaps3,
        "read_para": {},
        "reasonable_value": [0, 1000],
        "operation":None,
        "operation_para": {},
        "time_type": "BT",
    },
    "fo_data":{
        "ECMWF": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\ECMWF_HR\rain24",
            "dir_fo": r"O:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour":[8,20,12],
            "dtime":[0,241,12],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.change,
            "operation_para": {"used_coords": "dtime", "delta": 24},
            "time_type": "BT",
            "move_fo_time": 12
        },

        "Forecaster": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Forecaster\rain24",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\RAIN24\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[24,241,24],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": None,
            "time_type": "BT",
            "move_fo_time": 0
        },
        "Province": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Province\rain24",
            "dir_fo": r"O:\data\grid\NWFD_SMERGE\RAIN03\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[3,241,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.sum_of_sta,
            "operation_para":  {"used_coords": ["dtime"], "span": 24},
            "time_type": "BT",
            "move_fo_time": 0
        },
        "ObjectiveMethod": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\ObjectiveMethod\rain24",
            "dir_fo": r"\\10.20.90.107\sm_qpf\combine_24h\sfc\YYYYMMDDHH\YYYYMMDDHH.TTT.m4",
            "hour": [8, 20, 12],
            "dtime": [24, 241, 12],
            "read_method": meteva.base.io.read_griddata_from_micaps4,
            "read_para": {},
            "operation": None,
            "operation_para": None,
            "time_type": "UT",
            "move_fo_time": 12
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
    #meteva.base.io.print_gds_file_values_names(file)
    #meteva.base.print_gds_file_values_names(filename)
    meteva.product.prepare_dataset(para_example)
    #combine_file = r"H:\task\other\202009-veri_objective_method\combine_24h.hdf"
    #df = pd.read_hdf(combine_file)
    #print(df)

    #hdf_file = r"H:\task\other\202009-veri_objective_method/summer.h5"
    #hdf_file = r"H:\task\other\202009-veri_objective_method\Forecaster\rain24\summer.h5"
    #sta_all_f  = pd.read_hdf(hdf_file)
    #print(sta_all_f)
    #hdf_file = r"H:\task\other\202009-veri_objective_method\ob_rain01\summer.h5"
    #sta_all_ob = pd.read_hdf(hdf_file)
    #print(sta_all_ob)
    #hdf_file = r"H:\task\other\202009-veri_objective_method\ECMWF_HR\rain24\summer.h5"
    #sta_all_ec = pd.read_hdf(hdf_file)
    #print(sta_all_ec)

    #sta_all = meb.combine_on_obTime_id(sta_all_ob,[sta_all_f,sta_all_ec])
    #sta_all = pd.read_hdf(hdf_file)
    #sta_all = meb.sele.not_IV(sta_all)
    #print(sta_all)
    #mpd.score(sta_all,mem.bias,grade_list= [1,10,25,50,100],g = "dtime",plot = "bar",dpi = 100,save_path=r"H:\task\other\202009-veri_objective_method/bias.png")