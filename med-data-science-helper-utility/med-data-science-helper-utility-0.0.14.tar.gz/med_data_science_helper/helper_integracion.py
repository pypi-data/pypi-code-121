# -*- coding: utf-8 -*-
"""
Created on Thu Dec  2 21:49:23 2021

@author: User
"""
import numpy as np
import pandas as pd

#import core_helper.helper_general as hg
#hg.set_base_path()


#import src.Prj_Core.core_helper.helper_transformers as ht
#import src.Prj_Core.core_helper.helper_output as ho
#import src.Prj_Core.core_helper.helper_acces_db as hadb
#import src.Prj_Core.core_helper.helper_dataframe as hd
#import src.Prj_Core.core_helper.helper_clean as hc
#import src.Prj_Core.core_helper.helper_siagie_kpi as hsk
#import src.Prj_Core.core_helper.helper_terceros_kpi as htk
#import src.Prj_Core.core_helper.helper_feature_selection as hfs

import data_science_helper.helper_general as hg
import data_science_helper.helper_transformers as ht
import data_science_helper.helper_output as ho
import data_science_helper.helper_dataframe as hd
import data_science_helper.helper_clean as hc
import data_science_helper.helper_feature_selection as hfs


import med_data_science_helper.helper_acces_db as hadb
import med_data_science_helper.helper_siagie_kpi as hsk
import med_data_science_helper.helper_terceros_kpi as htk



def get_df_estructura_base(**kwargs):
    
    with ho.pretty_output(ho.FG_BLUE) as out:
        out.write('get_df_estructura_base')        
    
    dtypes_columns = {'COD_MOD': str,
                      'ANEXO':int,                    
                      'COD_MOD_T_MENOS_1':str,
                      'ANEXO_T_MENOS_1':int,                      
                      'UBIGEO_NACIMIENTO_RENIEC':str,
                      'N_DOC':str,
                      'ID_GRADO':int,
                      'ID_PERSONA':int,#nurvo
                      'CODIGO_ESTUDIANTE':str,
                      'NUMERO_DOCUMENTO':str,
                      'NUMERO_DOCUMENTO_APOD':str,
                      'CODOOII':str
                      }  
    
    anio = kwargs["anio"]
    
    if anio < 2016:
        anio_serv = None
    else:
        anio_serv = anio
    
    df_servicios = hadb.get_df_servicios(macro_region=kwargs["macro_region"],anio=anio_serv)  
    df_id_persona = kwargs["df_id_persona"]
    path_est_base = kwargs["path_base"]
    list_pd = []
    #5,6,7,8
    for ID_GRADO in kwargs["grupo_grados"]:
        url = hg.get_base_path()+path_est_base
        url = url.format(ID_GRADO,kwargs["anio"] )
        df =pd.read_csv(url, dtype=dtypes_columns ,encoding="utf-8")
        df['STR_ID_GRADO'] = "GRADO_" + str(ID_GRADO)      
        df = pd.merge(df,df_servicios, left_on=["COD_MOD","ANEXO"], right_on = ["COD_MOD","ANEXO"] ,how="inner")
        if df_id_persona is not None:
            df = pd.merge(df,df_id_persona[["ID_PERSONA"]], left_on="ID_PERSONA", right_on = "ID_PERSONA",how="inner")        
        list_pd.append(df)
        
    df_reg = pd.concat(list_pd)
    
    
    return df_reg

def transform_df(**kwargs):
   
    
    df_reg = kwargs["df_reg"]
    ID_P_T = df_reg['ID_PERSONA'] 
    df_reg.drop(columns = ['ID_PERSONA'] ,inplace = True) 
    
    col_name_y = kwargs["col_name_y"]
    feature_selection = kwargs["feature_selection"]
    max_cat = 15
    list_cl_cat_many_cat = hd.get_cat_columns_many_cats(df_reg,min_nunique=max_cat)
    
    ho.print_message('Eliminando columnas con categorias mayor a : {}'.format(max_cat))

    df_reg.drop(columns = list_cl_cat_many_cat,inplace = True) 
    for cat_with_many in list_cl_cat_many_cat:
        print("many categories : {}".format(cat_with_many))
    
    ho.print_message('Eliminando columnas con muchos missing')
    df_reg = hfs.drop_nan_columns(df_reg)
    
    list_cat_cls = hd.get_cat_columns(df_reg)
    list_cat_cls_with_nan = []
    
    for cat in list_cat_cls:
        tiene_missing = df_reg[cat].isnull().values.any()
        if tiene_missing:
            list_cat_cls_with_nan.append(cat)
    if(len(list_cat_cls_with_nan)>0):
        ho.print_message('Generando categoria NAN para los missing')

        df_reg = hc.fill_nan_with_nan_category_in_cls(df_reg , list_cat_cls_with_nan)

        
    df_reg = hc.trim_category_cls(df_reg)
          
    if col_name_y is not None:
        y = df_reg[col_name_y]
        df_reg.drop(columns = [col_name_y] ,inplace = True) 
        #columns_to_drop_all.append(col_name_y)
    else:    
        y = None
               
    
    #X = df_reg.drop(columns = columns_to_drop_all) 
    X = df_reg.copy()
   
    ho.print_message('Generando columnas binarias para las siguientes columnas:')
    ct = ht.CatTransformer(pp = "lb",console=True) #lb le
    ct.fit(X)
    X_t = ct.transform(X)
    #print(X_t.columns)
    if feature_selection:
        ho.print_message('e).feature_selection: filtrando variables irrelevantes')
        X_t = hfs.drop_cls_unique_value(X_t)
        X_t = hfs.drop_corr_columns(X_t)
              
        
    return ID_P_T,X_t, y
    