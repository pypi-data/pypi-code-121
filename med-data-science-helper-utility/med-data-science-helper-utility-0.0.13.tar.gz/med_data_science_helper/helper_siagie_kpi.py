# -*- coding: utf-8 -*-
"""
Created on Sun Mar 21 12:21:41 2021

@author: User
"""

import numpy as np
import pandas as pd
from functools import reduce
#from core_helper import helper_acces_db as hadb

#import core_helper.helper_acces_db as hadb
#from core_helper import helper_dataframe as hdf
#import core_helper.helper_general as hg
#import core_helper.helper_output as ho
#import core_helper.helper_clean as hc
#import src.Prj_Core.core_helper.helper_cache as hch


import med_data_science_helper.helper_acces_db as hadb
from data_science_helper import helper_dataframe as hdf
import data_science_helper.helper_general as hg
import data_science_helper.helper_output as ho
import data_science_helper.helper_clean as hc
import data_science_helper.helper_cache as hch

'''
df_siagie = hadb.get_siagie_por_anio(2022,columns_n= ['ID_PERSONA'])
print(df_siagie.shape)
df = hadb.get_juntos(2019)
print(df.PERIODO.unique())
df_siagie2 = agregar_pivot_juntos(df_siagie, anio_df=2022,anio_h=2021,t_anios=3,cache=True)
print(df_siagie2.columns)
print(df_siagie2.VCC_1_T.value_counts())
print(df_siagie2.VCC_1_T_MENOS_1.value_counts())
'''

def gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios):
    
    if(t_anios < 1):            
        msg = "ERROR: El numero t_anios debe ser mayor a 0"
        raise Exception(msg)
        
    ultimo_anio =anio_h- t_anios
    ultimo_anio_data = ultimo_anio + 1    
    
    if(ultimo_anio_data<2014):            
        msg = "ERROR: Se pretende consultar hasta el anio "+str(ultimo_anio_data)+", solo se tiene data hasta el 2014"      
        raise Exception(msg)   

    if(anio_h>anio_df):            
        msg = "ERROR: El parametro anio_h no puede ser mayor al parametro anio_h "        
        raise Exception(msg)   
        
    num = anio_df-anio_h
    
    return ultimo_anio , num


def get_kpi_foraneo(df,anio_df=None, anio_h=None ,t_anios=1,modalidad="EBR",cache=False):
    
    filename = 'kpi_foraneo'
    ho.print_message('agregar_kpi_foraneo')
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad])
    print(key_cache)
    if cache:
        df_final_total = hch.get_cache(filename,key_cache)
        if df_final_total is not None:
            ho.print_items(df_final_total.columns)
            if df is None:
                return 
            else:
                df = pd.merge(df, df_final_total, left_on="ID_PERSONA",  right_on="ID_PERSONA",  how='left')
                return df
    
    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios) 
    ultimo_anio_data = ultimo_anio + 1 
    if(ultimo_anio_data<2016):            
        msg = "ERROR: Se pretende consultar hasta el anio "+str(ultimo_anio_data)+", solo se tiene data hasta el 2016"     
        raise Exception(msg) 
    
    #df_id_persona = df[["ID_PERSONA"]].copy()
    df_id_persona = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA'])
    
    
    url = hadb.get_path_BD()+"\\06.ubigeo_peru\\ubigeo_distrito.csv" 

    dtypes_columns = {'reniec':str, 'inei':str }
    df_reniec_ubigeo = pd.read_csv(url,encoding="latin-1",usecols=["reniec","inei"],dtype=dtypes_columns)

    list_df=[]
    
    for anio in range(anio_h,ultimo_anio,-1):
        

        col_name="FORANEO_{}_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name = col_name+posfix
            #cols_to_drop_desap.append(col_name.format("TOTAL","DESAPROBADO"))
            #cols_to_drop_reti.append(col_name.format("TOTAL","RETIRADO"))

        #cols_to_sum_desap.append(col_name.format("TOTAL","DESAPROBADO"))
        #cols_to_sum_reti.append(col_name.format("TOTAL","RETIRADO"))
        
    
        df_estudiantes =  hadb.get_siagie_por_anio(anio,
                                                   columns_n=["ID_PERSONA","UBIGEO_NACIMIENTO_RENIEC","COD_MOD","ANEXO"])

        df_merged = pd.merge(df_estudiantes,df_reniec_ubigeo,left_on="UBIGEO_NACIMIENTO_RENIEC",right_on="reniec",how="left")
        
        df_merged = pd.merge(df_id_persona,df_merged,left_on="ID_PERSONA",right_on="ID_PERSONA",how="left")

        df_serv = hadb.get_df_servicios(anio=anio,geo=True)[["COD_MOD","ANEXO","CODGEO"]]
        df_final = pd.merge(df_merged,df_serv,left_on=["COD_MOD","ANEXO"],right_on=["COD_MOD","ANEXO"],how="inner")

        df_final.loc[(df_final['inei'].isna()), col_name.format("DIST")] = np.nan
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei']==df_final['CODGEO']), col_name.format("DIST")] = 0
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei']!=df_final['CODGEO']), col_name.format("DIST")] = 1

        df_final.loc[(df_final['inei'].isna()), col_name.format("PROV")] = np.nan
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei'].str[:4]==df_final['CODGEO'].str[:4]), col_name.format("PROV")] = 0
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei'].str[:4]!=df_final['CODGEO'].str[:4]), col_name.format("PROV")] = 1

        df_final.loc[(df_final['inei'].isna()), col_name.format("DEP")] = np.nan
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei'].str[:2]==df_final['CODGEO'].str[:2]), col_name.format("DEP")] = 0
        df_final.loc[(df_final['inei'].isna()==False) & (df_final['inei'].str[:2]!=df_final['CODGEO'].str[:2]), col_name.format("DEP")] = 1
        df_final.drop(['UBIGEO_NACIMIENTO_RENIEC', 'COD_MOD', 'ANEXO', 'inei', 'reniec', 'CODGEO'], axis=1,inplace=True)
        list_df.append(df_final)
        
        num+=1
        
    df_final_total = reduce(lambda left,right: pd.merge(left,right,on="ID_PERSONA"), list_df)
    ho.print_items(df_final_total.columns)
    hch.save_cache(df_final_total,filename,key_cache)
    if df is None:
        return 
    else:  
        df = pd.merge(df, df_final_total, left_on="ID_PERSONA",  right_on="ID_PERSONA",  how='left')
        return df



def generar_kpis_agg_servicios(df,anio_df=None , anio_h =None ,t_anios=1,modalidad="EBR",cache=False):
    
    filename = 'kpis_agg_servicios'
    ho.print_message('agregar_kpis_agg_servicios')
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns, excepto=["COD_MOD","ANEXO"])            
            if df is None:
                return 
            else:
                df = pd.merge(df, df_final, left_on=["COD_MOD","ANEXO"],  right_on=["COD_MOD","ANEXO"],  how='left')
            return df

    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios)

    df_serv = hadb.get_df_servicios(anio=anio_df,columns=["COD_MOD","ANEXO"])
    
    cols_to_sum_desap = []
    cols_to_sum_reti = []
    list_df_agg=[]
    cols_to_drop_desap = []
    cols_to_drop_reti = []
    for anio in range(anio_h,ultimo_anio,-1):

        if(anio<=2013):
                break

        col_name="{}_{}_SERVICIO_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name = col_name+posfix
            cols_to_drop_desap.append(col_name.format("TOTAL","DESAPROBADO"))
            cols_to_drop_reti.append(col_name.format("TOTAL","RETIRADO"))

        cols_to_sum_desap.append(col_name.format("TOTAL","DESAPROBADO"))
        cols_to_sum_reti.append(col_name.format("TOTAL","RETIRADO"))

        df_alum =  hadb.get_siagie_por_anio(anio, columns_n= ['ID_PERSONA','COD_MOD','ANEXO','SITUACION_FINAL'])
        df_alum = hc.trim_category_cls(df_alum)
        dic_valores = {
         'TOTAL_DESAPROBADO' : np.where(df_alum['SITUACION_FINAL']=='DESAPROBADO', 1,0)  ,
         'TOTAL_RETIRADO' : np.where(df_alum['SITUACION_FINAL']=='RETIRADO', 1,0)  ,    
         'TOTAL_ESTUDIANTES':1,
        }

        agg_config = {
         'TOTAL_DESAPROBADO':'sum',
         'TOTAL_RETIRADO':'sum', 
         'TOTAL_ESTUDIANTES':'sum',
        }

        df_agg = df_alum.assign(
        **dic_valores        
        ).groupby(['COD_MOD','ANEXO']).agg(agg_config).reset_index()

        df_agg_serv = pd.merge(df_serv,df_agg, 
                               left_on=["COD_MOD","ANEXO"], 
                               right_on = ["COD_MOD","ANEXO"] ,how="left")

        df_serv_anio_n = hadb.get_df_servicios(anio=anio,columns=["COD_MOD","ANEXO",'TALUMNO', 'TDOCENTE', 'TSECCION'])
 
        df_agg_serv = pd.merge(df_agg_serv,df_serv_anio_n, 
                               left_on=["COD_MOD","ANEXO"], 
                               right_on = ["COD_MOD","ANEXO"] ,how="left")


        df_agg_serv['RATIO_ALUMNO_DOCENTE'] = np.round(df_agg_serv['TALUMNO']/df_agg_serv['TDOCENTE'], decimals = 1)
        df_agg_serv['RATIO_SECCION_DOCENTE'] = np.round(df_agg_serv['TSECCION']/df_agg_serv['TDOCENTE'], decimals = 1)
        df_agg_serv.rename(columns={'TALUMNO': col_name.format("TOTAL","ALUMNO")}, inplace=True)
        df_agg_serv.rename(columns={'TDOCENTE': col_name.format("TOTAL","DOCENTE")}, inplace=True)
        df_agg_serv.rename(columns={'TSECCION': col_name.format("TOTAL","SECCION")}, inplace=True)
        
        df_agg_serv.rename(columns={'TALUMNO': col_name.format("TOTAL","ALUMNO")}, inplace=True)
        df_agg_serv.rename(columns={'TDOCENTE': col_name.format("TOTAL","DOCENTE")}, inplace=True)
        df_agg_serv.rename(columns={'TSECCION': col_name.format("TOTAL","SECCION")}, inplace=True)
        
        df_agg_serv.rename(columns={'RATIO_ALUMNO_DOCENTE': col_name.format("RATIO","ALUMNO_DOCENTE")}, inplace=True)
        df_agg_serv.rename(columns={'RATIO_SECCION_DOCENTE': col_name.format("RATIO","SECCION_DOCENTE")}, inplace=True)
                        
        df_agg_serv['RATIO_DESAPROBADOS'] = np.round(df_agg_serv['TOTAL_DESAPROBADO']/df_agg_serv['TOTAL_ESTUDIANTES'], decimals = 1)
        df_agg_serv['RATIO_RETIRADO'] = np.round(df_agg_serv['TOTAL_RETIRADO']/df_agg_serv['TOTAL_ESTUDIANTES'], decimals = 1)
        
        df_agg_serv.drop(['TOTAL_ESTUDIANTES'], axis=1,inplace=True)
        #df_agg_serv.rename(columns={'TOTAL_ESTUDIANTES': col_name.format("TOTAL","ESTUDIANTES")}, inplace=True)
        
        df_agg_serv.rename(columns={'RATIO_DESAPROBADOS': col_name.format("RATIO","DESAPROBADO")}, inplace=True)
        df_agg_serv.rename(columns={'RATIO_RETIRADO': col_name.format("RATIO","RETIRADO")}, inplace=True)
        
        df_agg_serv.rename(columns={'TOTAL_DESAPROBADO': col_name.format("TOTAL","DESAPROBADO")}, inplace=True)
        df_agg_serv.rename(columns={'TOTAL_RETIRADO': col_name.format("TOTAL","RETIRADO")}, inplace=True)


        list_df_agg.append(df_agg_serv)

        num+=1


    df_final = reduce(lambda left,right: pd.merge(left,right,on=["COD_MOD","ANEXO"]), list_df_agg)
   
    
    df_final['TOTAL_DESAPROBADO_SERVICIO'] = df_final[cols_to_sum_desap].sum(axis=1)
    df_final['MEAN_DESAPROBADO_SERVICIO'] = df_final[cols_to_sum_desap].mean(axis=1)
    df_final['STD_DESAPROBADO_SERVICIO'] = df_final[cols_to_sum_desap].std(axis=1)

    df_final['TOTAL_RETIRADO_SERVICIO'] = df_final[cols_to_sum_reti].sum(axis=1)
    df_final['MEAN_RETIRADO_SERVICIO'] = df_final[cols_to_sum_reti].mean(axis=1)
    df_final['STD_RETIRADO_SERVICIO'] = df_final[cols_to_sum_reti].std(axis=1)
    
    hch.save_cache(df_final,filename,key_cache)
    ho.print_items(df_final.columns, excepto=["COD_MOD","ANEXO"])
    if df is None:
        return 
    else:  
        df = pd.merge(df, df_final, left_on=["COD_MOD","ANEXO"],  right_on=["COD_MOD","ANEXO"],  how='left')
        return df

def generar_kpis_traslado(df,anio_df=None , anio_h =None ,t_anios=1,modalidad="EBR",cache=False):
    ho.print_message('generar_kpis_traslado')     
    filename = 'kpis_traslado'
    
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns)
            
            if df is None:
                return 
            else:
                df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
                return df
    
    
    #ID_PERSONA_SERIES = df['ID_PERSONA']
    ID_PERSONA_SERIES = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA'])
    
    #ultimo_anio =ANIO- T_ANIOS
    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios)
    #num = anio_df-anio_h
    #ultimo_anio =anio_h - t_anios
    #ultimo_anio_data = ultimo_anio + 1
    #num = 0
    list_df_m_tras = []
    cols_to_sum = []
    cols_to_drop = []
    for anio in range(anio_h,ultimo_anio,-1):
        if(anio<=2013):
            break
        col_name="TOTAL_TRASLADOS_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name = col_name+posfix
            cols_to_drop.append(col_name)
        cols_to_sum.append(col_name)
        df_m_t = pd.merge(ID_PERSONA_SERIES, hadb.get_traslados_por_anio(anio,modalidad),left_on="ID_PERSONA",
                          right_on="ID_PERSONA", how='left')
        df_m_t.fillna({'TOTAL_TRASLADOS':0}, inplace=True)
        df_m_t.rename(columns={'TOTAL_TRASLADOS': col_name}, inplace=True)
        list_df_m_tras.append(df_m_t)
        num+=1

    df_final = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras)
    df_final['TOTAL_TRASLADOS'] = df_final[cols_to_sum].sum(axis=1)
    df_final['MEAN_TRASLADOS'] = df_final[cols_to_sum].mean(axis=1)
    df_final['STD_TRASLADOS'] = df_final[cols_to_sum].std(axis=1)
    #print()
    df_final.drop(cols_to_drop, axis = 1,inplace=True)   
    

    ho.print_items(df_final.columns)
    hch.save_cache(df_final,filename,key_cache)
    #print(cols_to_sum)
    if df is None:
        return 
    else:    
        df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')        
        return df

def generar_kpis_traslado_a_publico(df,anio_df=None, anio_h =None ,t_anios=1,modalidad="EBR",cache=False):
    ho.print_message('generar_kpis_traslado_a_publico') 
    
    filename = 'kpis_traslado_a_publico'
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns) 
            
            if df is None:
                return 
            else:          
                df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
                return df    
        
    #if df_servicios is None:
    #    df_servicios = hadb.get_df_servicios()
    
    #ID_PERSONA_SERIES = df['ID_PERSONA']
    ID_PERSONA_SERIES = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA'])
    
    #ultimo_anio =ANIO- T_ANIOS
    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios)
    #num = 0
    list_df_m_tras = []
    cols_to_sum = []
    cols_to_drop = []
    for anio in range(anio_h,ultimo_anio,-1):
        if(anio<=2013):
            break
        col_name="TOTAL_TRASLADOS_A_PUBLICO_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name = col_name+posfix
            cols_to_drop.append(col_name)
        cols_to_sum.append(col_name)
        df_servicios = hadb.get_df_servicios(anio=anio)
        df_m_t = pd.merge(ID_PERSONA_SERIES, hadb.get_traslados_a_publico(anio,df_servicios,modalidad),left_on="ID_PERSONA",
                          right_on="ID_PERSONA", how='left')
        df_m_t.fillna({'TOTAL_TRASLADOS':0}, inplace=True)
        df_m_t.rename(columns={'TOTAL_TRASLADOS': col_name}, inplace=True)
        list_df_m_tras.append(df_m_t)
        num+=1

    df_final = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras)
    df_final['TOTAL_TRASLADOS_A_PUBLICO'] = df_final[cols_to_sum].sum(axis=1)
    df_final['MEAN_TRASLADOS_A_PUBLICO'] = df_final[cols_to_sum].mean(axis=1)
    df_final['STD_TRASLADOS_A_PUBLICO'] = df_final[cols_to_sum].std(axis=1)
    df_final.drop(cols_to_drop, axis = 1,inplace=True)    
    
    ho.print_items(df_final.columns)  
    hch.save_cache(df_final,filename,key_cache)
    
    if df is None:
        return 
    else:    
        df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')    
        return df


def generar_kpis_desercion(df,anio_df=None, anio_h=None ,t_anios=1,modalidad="EBR",cache=False):
    
    ho.print_message('generar_kpis_desercion')    
    
    filename = 'kpis_desercion'
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad])
    print(key_cache)
    if cache:
        df_final = hch.get_cache(filename,key_cache)
        if df_final is not None:
            ho.print_items(df_final.columns)
            if df is None:
                return 
            else:     
                df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
                return df    
    
    #ID_PERSONA_SERIES = df['ID_PERSONA']
    ID_PERSONA_SERIES = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA'])
    
    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios)
    #ultimo_anio =ANIO- T_ANIOS       
    #num = 1
    list_df_m_tras = []
    cols_to_sum = []
    cols_to_drop = []
    #ANIO = ANIO-1
    #print("anio_h : ",anio_h," ultimo_anio : ",ultimo_anio)
    for anio in range(anio_h,ultimo_anio,-1):
        #print("anio : ",anio)
        if(anio<=2013):
            break
        col_name="DESERTARA_DESPUES_DE_T"
        if(num>0):
            posfix="_MENOS_{}".format(num)
            col_name = col_name+posfix
            cols_to_drop.append(col_name)
        cols_to_sum.append(col_name)
        df_m_t = pd.merge(ID_PERSONA_SERIES, hadb.get_desertores_por_anio(anio,modalidad),left_on="ID_PERSONA",
                          right_on="ID_PERSONA", how='left')
        anios_str=str(anio)+"_"+str(anio+1)
        original_col = "DESERCION_"+anios_str

        df_m_t.fillna({original_col:0}, inplace=True)
        df_m_t.rename(columns={original_col: col_name}, inplace=True)

        list_df_m_tras.append(df_m_t)
        num+=1

    df_final = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras)
    df_final['TOTAL_DESERCIONES'] = df_final[cols_to_sum].sum(axis=1)
    df_final['MEAN_DESERCIONES'] = df_final[cols_to_sum].mean(axis=1)
    df_final['STD_DESERCIONES'] = df_final[cols_to_sum].std(axis=1)
    df_final.drop(cols_to_drop, axis = 1,inplace=True)    
    

    ho.print_items(df_final.columns)
    hch.save_cache(df_final,filename,key_cache)
    if df is None:
        return 
    else:    
        df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')    
        return df



def agregar_distancia_prim_sec(df,cache=False):
    

    ho.print_message('agregar_distancia_prim_sec')
    
    filename = 'distancia_prim_sec'
    key_cache = hch.get_key_cache(["distancia_prim_sec"])
    print(key_cache)
    if cache:
        df_dist = hch.get_cache(filename,key_cache)
        if df_dist is not None:
            ho.print_items(df_dist.columns,excepto=["COD_MOD","ANEXO"])
            if df is None:
                return 
            else:   
                df = pd.merge(df,df_dist, left_on=['COD_MOD','ANEXO'],right_on=['COD_MOD','ANEXO'], how='left')  
                return df  
    
    
    df_dist= hadb.get_distancia_prim_sec()    
    
    ho.print_items(df_dist.columns,excepto=["COD_MOD","ANEXO"])
    hch.save_cache(df_dist,filename,key_cache)
    
    if df is None:
        return 
    else:      
        df = pd.merge(df,df_dist, left_on=['COD_MOD','ANEXO'],right_on=['COD_MOD','ANEXO'], how='left')  
        return df




def generar_kpis_historicos(df,key_df="",anio_df=None,anio_h=None,cls_json=None,t_anios=0,
                            modalidad="EBR",cache=False,retornar=True):
    
    ho.print_message('generar_kpis_historicos')
    
    json_str = json_to_str(cls_json)
    
    filename = 'kpis_historicos'
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios,modalidad,json_str,key_df])
    print(key_cache)
    if cache: 
        df_final = hch.get_cache(filename,key_cache)
        #df_final = hdf.reduce_mem_usage(df_final)
        if df_final is not None:
            ho.print_items(df_final.columns)
            if df is None:
                #return df_final
                return
            else:   
                df_final = pd.merge(df , df_final, left_on=['ID_PERSONA'], right_on=['ID_PERSONA'], how='inner',suffixes=('','_repetido')) 
                return df_final    
    
    if(t_anios < 1):            
        msg = "ERROR: El numero t_anios debe ser mayor a 0"
        raise Exception(msg)
        #return False
    
    ultimo_anio =anio_h- t_anios
    ultimo_anio_data = ultimo_anio + 1
    if(ultimo_anio_data<2014):            
        msg = "ERROR: Se pretende consultar hasta el anio "+str(ultimo_anio_data)+", solo se tiene data hasta el 2014"      
        raise Exception(msg)   
    
    
    if(anio_h>anio_df):            
        msg = "ERROR: El parametro anio_h no puede ser mayor al parametro anio_h "        
        raise Exception(msg)  
    
    cls_list = []
    for key, value in cls_json.items():
        cls_list.append(key)  
        
    if 'ID_PERSONA' not in cls_list :
        cls_list.append('ID_PERSONA')
       
    ID_PERSONA_SERIES = df['ID_PERSONA']

    #df_final = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras)
    df_final,kpi_final_dic = get_df_final_kpis_historicos(ID_PERSONA_SERIES,anio_df,anio_h,ultimo_anio,cls_list,modalidad,cls_json)

    kpi_list = []
    for key, cls_anios in kpi_final_dic.items():
        kpi_list.append(key)   
        df_final = set_generic_kpis(df_final,key,cls_anios)
        #df_final.drop(cls_anios, axis = 1,inplace=True) 
    
    #df_final = hdf.reduce_mem_usage(df_final)
    ho.print_items(df_final.columns)
    hch.save_cache(df_final,filename,key_cache)
    
    if df is None:
        return 
    else:     
        df_final = pd.merge(df , df_final, left_on=['ID_PERSONA'], right_on=['ID_PERSONA'], how='inner',suffixes=('','_repetido'))    
        return df_final


def json_to_str(cls_json):
    list_value = ""
    for key,value in cls_json.items():   
        list_value=list_value+key[:2]+"_"
        if isinstance(value, list):
            listToStr = '_'.join([str(elem[:2]) for elem in value])
            list_value=list_value+listToStr+"_"
        else:
            list_value=list_value+value[:2]
    return list_value

def get_df_final_kpis_historicos(ID_PERSONA_SERIES,anio_df,anio_h,ultimo_anio,cls_list,modalidad,cls_json):
    
    
    
    num = anio_df-anio_h
    list_df_m_tras = []
    kpi_final_dic = {}
    
    for anio in range(anio_h,ultimo_anio,-1):
        if(anio<=2013):
            break

        #print("ANIO =================>>>>>>>>>  : ",anio)
        df_m_t = pd.merge(ID_PERSONA_SERIES, hadb.get_siagie_por_anio(anio,modalidad=modalidad,columns_n=cls_list),left_on="ID_PERSONA",
                          right_on="ID_PERSONA", how='left')
        
        df_m_t = hc.trim_category_cls(df_m_t)
        
        for key, values in cls_json.items():
            if  isinstance(values, list):
         
                #print("------------------category---------------------")
                for val in values:
                    key_val = key+"_"+val
                    if num ==0:
                        cl_pf = key_val+"_T"               
                    else:
                        cl_pf = key_val+"_T_MENOS_{}".format(num)                        
                    #df_m_t[cl_pf] = np.where((df_m_t[key]==val),1,0)
                    
                    df_m_t[cl_pf] = np.NaN 
                    df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==val), cl_pf] = 1
                    df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]!=val), cl_pf] = 0  
                    
                    #print(cl_pf)
                    if  (key_val in kpi_final_dic) ==False:
                        kpi_final_dic[key_val]=[]                    
                    kpi_final_dic[key_val].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 
            elif values=="dummy":      
                
                #print("-----------------dummy----------------------")
                if num ==0:
                    cl_pf = key+"_T"              
                else:
                    cl_pf = key+"_T_MENOS_{}".format(num)                
                #df_m_t[cl_pf] = np.where((df_m_t[key]==1),1,0)
                
                df_m_t[cl_pf] = np.NaN 
                df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==1), cl_pf] = 1
                df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==0), cl_pf] = 0   
                
                #print(cl_pf)
                
                if  (key in kpi_final_dic) ==False:
                    kpi_final_dic[key]=[]                    
                kpi_final_dic[key].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 
                
            elif values=="numero":    
                
                #print("-----------------numero----------------------")                
                if num ==0:
                    cl_pf = key+"_T"              
                else:
                    cl_pf = key+"_T_MENOS_{}".format(num)                
                #df_m_t[cl_pf] = df_m_t[key]  
                
                df_m_t[cl_pf] = np.NaN    
                df_m_t.loc[(df_m_t[key]!="NaN"), cl_pf] = df_m_t[key] 
                
                #print(cl_pf)
                if  (key in kpi_final_dic) ==False:
                    kpi_final_dic[key]=[]                    
                kpi_final_dic[key].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 
                
        df_m_t = hdf.reduce_mem_usage(df_m_t)
        list_df_m_tras.append(df_m_t)
        num+=1

    return reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras), kpi_final_dic







def set_generic_kpis(df,cl_name=None,cl_list=[],set_nan=False):

    if(set_nan==False):
        if(len(cl_list)>1):            
            #print("---------------------------------------") 
            t_cl_name = 'TOTAL_'+cl_name
            df[t_cl_name] = df[cl_list].sum(axis=1)
            #print(t_cl_name)
            
            m_cl_name = 'MEAN_'+cl_name
            df[m_cl_name] = df[cl_list].mean(axis=1)
            #print(m_cl_name)
            
            if(len(cl_list)>2):
                st_cl_name = 'STD_'+cl_name 
                df[st_cl_name] = df[cl_list].std(axis=1)
                #print(st_cl_name)
                
            mi_cl_name = 'MIN_'+cl_name    
            df[mi_cl_name] = df[cl_list].min(axis=1)
            #print(mi_cl_name)
            
            ma_cl_name = 'MAX_'+cl_name  
            df[ma_cl_name] = df[cl_list].max(axis=1)
            #print(ma_cl_name)
    else:
        df['TOTAL_'+cl_name] = np.nan
        df['MEAN_'+cl_name] = np.nan
        df['STD_'+cl_name] = np.nan
    return df



def agregar_notas(df,key_df="",anio_df=None,anio_notas=None,df_notas=None,
                  min_alumn_zscore=20,
                  cls_group=["NOTA","ZSCORE","AGG_CODMOD_GR","AGG_NOTA_ALUM"],notas_group="CM",cache=False):
    
    ho.print_message('agregar_notas')

    if df is None:
        msg = "ERROR: Debe proporcionar el DF de alumnos"
        raise Exception(msg)
    
    if 'ID_PERSONA' not in df.columns:
        msg = "ERROR: El dataframe df no tiene la columna ID_PERSONA"
        raise Exception(msg)
        
    filename = 'kpis_notas'
    key_cache = hch.get_key_cache([anio_df,anio_notas,min_alumn_zscore,notas_group]+cls_group+[key_df] )
    print(key_cache)
    if cache:
        df_alum_nota = hch.get_cache(filename,key_cache)
        if df_alum_nota is not None:
            ho.print_items(df_alum_nota.columns)   

            df_join_model = pd.merge(df , df_alum_nota, left_on=['ID_PERSONA'],  right_on=['ID_PERSONA'], how='left',suffixes=('','_x'))
            return df_join_model         
        
        
        
    
    if anio_df is None:
        msg = "ERROR: Debe especificar el año del df de alumnos"
        raise Exception(msg)
    
    if anio_notas is None:
        msg = "ERROR: Debe especificar el año de las notas"
        raise Exception(msg)
    
    if anio_notas>anio_df:
        print("ERROR: El anio de notas no puede ser mayor al anio del df de alumnos")
        raise Exception(msg)
    
    if df_notas is None:
        df_notas = hadb.get_df_notas(anio_notas)
    
    postfix = ""    
    if anio_df== anio_notas:
        postfix ="T"  
    else:
        resta = anio_df - anio_notas
        postfix ="T_MENOS_{}".format(resta)  
    #print("postfix : ",postfix)
    #print("---------df_notas------------")

    #print(df_notas.shape)


    
    #notas del anio t_menos_n de los alumnos del anio n
    df_notas_f = pd.merge(df_notas , df['ID_PERSONA'], left_on='ID_PERSONA', 
                          right_on='ID_PERSONA', how='inner')
    
    #print("---------df_notas_f------------")

    #print(df_notas_f.shape)
    
    #print("Total notas inicial : ",df_notas_f.shape)
    df_ser=df_notas_f.groupby(['COD_MOD', 'ANEXO']).size().reset_index()[['COD_MOD', 'ANEXO']]
    #hay que optener el listado total de alumnos del anio pasado para hacer los group_by respectivos con la data total de n-1.
    #estos alumnos deben pertenecer a los mismos servicios que los alumnos del anio n
    df_notas_alum_n_mes_1 = pd.merge(df_notas , df_ser, left_on=['COD_MOD','ANEXO'], 
                          right_on=['COD_MOD','ANEXO'], how='inner')
    
    df_notas_alum_n_mes_1 = hdf.reduce_mem_usage(df_notas_alum_n_mes_1)
    df_notas_f = hdf.reduce_mem_usage(df_notas_f)
    
    #print("---------df_notas_f------------")
    #print(df_notas_f.dtypes)
    #print(df_notas_f.shape)
    
    #print("---------df_notas_alum_n_mes_1------------")
    #print(df_notas_alum_n_mes_1.dtypes)
    #print(df_notas_alum_n_mes_1.shape)
    

    df_alum_nota = get_df_final_notas_alumn(df_notas_f,df_notas_alum_n_mes_1,postfix,min_alumn_zscore,cls_group,notas_group)
    #print("---------df_alum_nota------------")

    #print(df_alum_nota.shape)
    df_alum_nota = hdf.reduce_mem_usage(df_alum_nota)
    #print(df_alum_nota.dtypes)
    #print(df_alum_nota.shape)
    
 
    column_j_alum_not = ['ID_PERSONA']   
    
    list_area_letter = get_list_area_letter(notas_group)
    for a_l in list_area_letter:       
        df_alum_nota.rename(columns={get_NC(a_l): get_NC(a_l,postfix)}, inplace=True)
        df_alum_nota.rename(columns={get_MN(a_l): get_MN(a_l,postfix)}, inplace=True)
        df_alum_nota.rename(columns={get_SN(a_l): get_SN(a_l,postfix)}, inplace=True)
        
    df_alum_nota.rename(columns={'TOTAL_CURSOS_X_ALUMNO': 'TOTAL_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'TOTAL_CURSOS_VALIDOS_X_ALUMNO': 'TOTAL_CURSOS_VALIDOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'TOTAL_CURSOS_APROBADOS_X_ALUMNO': 'TOTAL_CURSOS_APROBADOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'MEAN_CURSOS_X_ALUMNO': 'MEAN_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'STD_CURSOS_X_ALUMNO': 'STD_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
          
    if 'TOTAL_ALUMNOS_X_CODMOD_NVL_GR' in df_alum_nota:
        del df_alum_nota['TOTAL_ALUMNOS_X_CODMOD_NVL_GR']
        #print("---------------------")
  
    notas_selected = list_area_letter
    
    
    list_cls = []
    #print("**********COLUMNAS GENERADAS****************")
    for group in cls_group:
        if group == "NOTA":
            #print("NOTA")
            list_notas_cls = df_alum_nota.loc[:,df_alum_nota.columns.str.startswith('NOTA_')].columns
            notas_selected_ = get_notas_prefix_by_gp("NOTA_",notas_selected)         
            sub_list = [sa for sa in list_notas_cls if any(sb in sa for sb in notas_selected_)]
            #print(sub_list)
            list_cls.append(sub_list)
            #print("*******************************************************")
        if group == "ZSCORE":
            #print("ZSCORE")
            list_zscore_cls = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('Z_NOTA')].columns    
            notas_selected_ = get_notas_prefix_by_gp("Z_NOTA_",notas_selected) 
            sub_list = [sa for sa in list_zscore_cls if any(sb in sa for sb in notas_selected_)]
            #print(sub_list)
            list_cls.append(sub_list)
            #print("********************************************************")
        if group == "AGG_CODMOD_GR":
            #print("AGG_CODMOD_GR")
            list_agg_codmod_cls = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('CODMOD_NVL_GR')].columns 
            notas_selected_ = [ s + '_X_CODMOD_NVL_GR' for s in notas_selected ]             
            sub_list = [sa for sa in list_agg_codmod_cls if any(sb in sa for sb in notas_selected_)]
            #print(sub_list)
            list_cls.append(sub_list)
            #print("*********************************************************")
        if group == "AGG_NOTA_ALUM":
            #print("AGG_NOTA_ALUM")
            sub_list = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('CURSOS')].columns
            #print(sub_list)
            list_cls.append(sub_list)
            #print("*********************************************************")
            
             
    
    list_cls = hg.flat_list(list_cls) 
    #print("----------final--------------")
    #print(list_cls)
    #print("----------final--------------")
    
    ho.print_items(list_cls,excepto=[])
 
    
    list_cls.append('ID_PERSONA')   
    
    hch.save_cache(df_alum_nota[list_cls],filename,key_cache)
    
    
    df_join_model = pd.merge(df , df_alum_nota[list_cls], left_on=['ID_PERSONA'], 
                             right_on=column_j_alum_not, how='left',suffixes=('','_x'))

    df_join_model = hdf.reduce_mem_usage(df_join_model)
    
    #creando dummy que indica si el zscore esta nullo o no
    list_area_letter = notas_selected
    for a_l in list_area_letter:
        if ("ZSCORE" in cls_group): 
            hc.agregar_na_cls(df_join_model,get_ZN(a_l,postfix))
        
    return df_join_model

def get_notas_by_gp(notas_gp):
    cm_notas = ["C","M"]
    short_notas = cm_notas + ["F","R"]
    B0_notas = ["P","T","Y","S","L"]
    F0_notas = ["E","D","G","I","A","H","B"]
    full_notas = short_notas+B0_notas+F0_notas
    B0_notas = short_notas + B0_notas
    F0_notas = short_notas + F0_notas  
    
    if notas_gp=="COMMON":
        notas  = short_notas
    elif notas_gp=="FULL":
        notas  = full_notas 
    elif notas_gp=="B0":
        notas  = B0_notas
    elif notas_gp=="F0":
        notas  = F0_notas
    elif notas_gp=="CM":
        notas  = cm_notas
        
    return notas
    
def get_notas_prefix_by_gp(prefix,notas_selected):

    notas_con_prefijo = [prefix + s for s in notas_selected ] 
    return notas_con_prefijo


    '''
    cm_notas = ["C","M"]
    short_notas = cm_notas + ["F","R"]
    B0_notas = ["P","T","Y","S","L"]
    F0_notas = ["E","D","G","I","A","H","B"]
    full_notas = short_notas+B0_notas+F0_notas
    B0_notas = short_notas + B0_notas
    F0_notas = short_notas + F0_notas   
    
    if notas_cls=="SHORT":
        common_zscore = [prefix + s for s in short_notas ] 
    elif notas_cls=="FULL":
        common_zscore = [prefix + s for s in full_notas ] 
    elif notas_cls=="B0":
        common_zscore = [prefix + s for s in B0_notas ] 
    elif notas_cls=="F0":
        common_zscore = [prefix + s for s in F0_notas ] 
    elif notas_cls=="CM":
        common_zscore = [prefix + s for s in cm_notas ] 
    
    return common_zscore
    '''

def get_df_final_notas_alumn(df_notas_f,df_notas_alum_n_mes_1,postfix,min_alumn,cls_group,notas_group):
    #print(df_notas_f.dtypes)
    df_a = get_df_por_alum(df_notas_f,notas_group,cls_group)
    df_a.reset_index(inplace=True)
    df_a['COD_MOD']=df_a['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    df_a['ANEXO']=df_a['ANEXO'].astype('int')

    #dataSet_por_alumno.head()
    #["NOTA","ZSCORE","AGG_CODMOD_GR","AGG_NOTA_ALUM"]

    if ("ZSCORE"  in cls_group or "AGG_CODMOD_GR"  in cls_group or "AGG_NOTA_ALUM"  in cls_group):

        dataSet_por_nivel_grado_serv, dataSet_por_nivel_grado = get_df_por_grado_serv(df_notas_alum_n_mes_1)
        
        #print(dataSet_por_nivel_grado)
        
        dataSet_por_nivel_grado_serv.reset_index(inplace=True)
        dataSet_por_nivel_grado_serv['COD_MOD']=dataSet_por_nivel_grado_serv['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
        dataSet_por_nivel_grado_serv['ANEXO']=dataSet_por_nivel_grado_serv['ANEXO'].astype('int')
        #dataSet_por_nivel_grado.head()
        #print(df_a.dtypes)
        #print("**********************************")
        #print(dataSet_por_nivel_grado_serv.dtypes)
    
        #print("df_a 1>",df_a.shape)
        df_a = pd.merge(df_a, dataSet_por_nivel_grado_serv, left_on=["COD_MOD","ANEXO"],  right_on=["COD_MOD","ANEXO"],  how='inner')
        #print("df_a 2>",df_a.shape)
        
        list_area_letter = get_list_area_letter(notas_group)
    
        #calculamos el z score por alumno a nivel de grado servicio
        for a_l in list_area_letter:
            df_a[get_ZN(a_l,postfix)] = (df_a[get_NC(a_l)] - df_a[get_MN(a_l)])/df_a[get_SN(a_l)]
        
        #si el zscore no se puede calcular por el numero de alumnos a nivel de grado servicio, 
        #entonces se calculara a nivel de grado region
        #adicionalmente se crea una columna que indica para que alumnos se imputo con el z score a nivel grado region
        if len(dataSet_por_nivel_grado) > 0:
            for a_l in list_area_letter:        
    
                mean = dataSet_por_nivel_grado.iloc[0][get_MN(a_l)]
                std = dataSet_por_nivel_grado.iloc[0][get_SN(a_l)]
    
                #df_a[get_ZN_I(a_l,postfix)] = np.where((df_a[get_ZN(a_l,postfix)].isna()) & (df_a[get_NC(a_l)].isna()==False), 1,0)
                #df_a.loc[(df_a[get_ZN(a_l,postfix)].isna()) & (df_a[get_NC(a_l)].isna()==False), get_ZN(a_l,postfix)] = (df_a[get_NC(a_l)]-mean)/std    
                df_a[get_ZN_I(a_l,postfix)] = np.where( (df_a[get_NC(a_l)].isna()==False) & (df_a['TOTAL_ALUMNOS_X_CODMOD_NVL_GR']<= min_alumn) , 1,0)
                df_a.loc[ (df_a[get_NC(a_l)].isna()==False) & (df_a['TOTAL_ALUMNOS_X_CODMOD_NVL_GR']<= min_alumn), get_ZN(a_l,postfix)] = (df_a[get_NC(a_l)]-mean)/std    
    
                df_a[get_ZN_I(a_l,postfix)] = np.where( (df_a[get_NC(a_l)].isna()==False) & (df_a[get_SN(a_l)]== 0) , 1,0)
                df_a.loc[ (df_a[get_NC(a_l)].isna()==False) & (df_a[get_SN(a_l)]== 0), get_ZN(a_l,postfix)] = (df_a[get_NC(a_l)]-mean)/std    
    

    #nos quedamos con las notas en el ultimo servicio cursado
    df_a.drop_duplicates(subset ="ID_PERSONA", keep = "last", inplace = True)
    
    return df_a




    


def get_df_por_grado_serv(df_notas_f):
    
    #notas por codigo modular anexo
    df_notas_por_grado_serv =  get_df_notas_por_groupby(df_notas_f)
    
    
    #notas por alumno
    df_notas_f['dummy']=1
    df_notas_por_grado =  get_df_notas_por_groupby(df_notas_f,groupby=['dummy'],agg_label='CODMOD_NVL_GR')
    
    return df_notas_por_grado_serv, df_notas_por_grado




def get_df_notas_por_groupby(df_notas_f,groupby=['COD_MOD','ANEXO'],agg_label='CODMOD_NVL_GR'):
    #print(df_notas_f.columns)
    dataSet_por_nivel_grado = df_notas_f.assign(   

    ############## mean ##############   
     #A3 A2 A5  B0 F0
     MEAN_NOTA_C_X_CODMOD_NVL_GR =  np.where(df_notas_f['DA']=='C', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN),  
        
     MEAN_NOTA_M_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='M',
                                            df_notas_f['NOTA_AREA_REGULAR'],np.NaN),
        
     MEAN_NOTA_P_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='P',
                                            df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     MEAN_NOTA_T_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='T',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_Y_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='Y',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     MEAN_NOTA_F_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='F',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
           
     MEAN_NOTA_R_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='R',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_S_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='S',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     
     MEAN_NOTA_L_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='L',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     
     MEAN_NOTA_E_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='E',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     MEAN_NOTA_D_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='D',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     MEAN_NOTA_G_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='G',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     
     MEAN_NOTA_I_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='I',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     MEAN_NOTA_A_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='A',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     MEAN_NOTA_H_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='H',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     MEAN_NOTA_B_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='B',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_O_X_CODMOD_NVL_GR =   np.where((df_notas_f['DA']=='O') &                                                  
                                              (df_notas_f['NOTA_AREA_REGULAR']>=0),
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     ############## std ##############   
     #A3 A2 A5  B0 F0
     STD_NOTA_C_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='C', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_M_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='M', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_P_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='P', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     STD_NOTA_T_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='T', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_Y_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='Y', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_F_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='F', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_R_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='R', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     STD_NOTA_S_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='S', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_L_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='L', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_E_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='E', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_D_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='D', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
          
     STD_NOTA_G_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='G', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_I_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='I', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_A_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='A', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     STD_NOTA_H_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='H', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN),      
     
     STD_NOTA_B_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='B', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
        
     STD_NOTA_O_X_CODMOD_NVL_GR =   np.where((df_notas_f['DA']=='O') &                                              
                                                 (df_notas_f['NOTA_AREA_REGULAR']>=0),
                                                  df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     TOTAL_ALUMNOS_X_CODMOD_NVL_GR = df_notas_f['ID_PERSONA']

    ).groupby(groupby).agg({
                                        'MEAN_NOTA_C_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_M_X_{}'.format(agg_label):'mean',  
                                        'MEAN_NOTA_P_X_{}'.format(agg_label):'mean', 
                                        'MEAN_NOTA_T_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_Y_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_F_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_R_X_{}'.format(agg_label):'mean',                                        
                                        'MEAN_NOTA_S_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_L_X_{}'.format(agg_label):'mean',                                        
                                        'MEAN_NOTA_E_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_D_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_G_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_I_X_{}'.format(agg_label):'mean',                                        
                                        'MEAN_NOTA_A_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_H_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_B_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_O_X_{}'.format(agg_label):'mean',
        
                                        'STD_NOTA_C_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_M_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_P_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_T_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_Y_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_F_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_R_X_{}'.format(agg_label):'std',                                        
                                        'STD_NOTA_S_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_L_X_{}'.format(agg_label):'std',                                          
                                        'STD_NOTA_E_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_D_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_G_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_I_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_A_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_H_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_B_X_{}'.format(agg_label):'std',   
                                        'STD_NOTA_O_X_{}'.format(agg_label):'std',  
                                        
                                        'TOTAL_ALUMNOS_X_{}'.format(agg_label):'nunique', 
                                       })
    
    #dataSet_por_nivel_grado['COD_MOD']=dataSet_por_nivel_grado['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    #dataSet_por_nivel_grado['ANEXO']=dataSet_por_nivel_grado['ANEXO'].astype('int')

    return dataSet_por_nivel_grado



def get_df_por_alum(df_notas_f,notas_group,cls_group):
    
    
    if notas_group == 'CM':
        
        dic_valores = {
         'NOTA_C_X_ALUMNO' : np.where(df_notas_f['DA']=='C',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_M_X_ALUMNO' : np.where(df_notas_f['DA']=='M',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
        } 
        agg_config = {
         'NOTA_C_X_ALUMNO':'mean',
         'NOTA_M_X_ALUMNO':'mean', 
        }  
        
    elif notas_group == 'COMMON':
        
        dic_valores = {
         'NOTA_C_X_ALUMNO' : np.where(df_notas_f['DA']=='C',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_M_X_ALUMNO' : np.where(df_notas_f['DA']=='M',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_F_X_ALUMNO' : np.where(df_notas_f['DA']=='F',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_R_X_ALUMNO' : np.where(df_notas_f['DA']=='R',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
        } 
        agg_config = {
         'NOTA_C_X_ALUMNO':'mean',
         'NOTA_M_X_ALUMNO':'mean', 
         'NOTA_F_X_ALUMNO':'mean',
         'NOTA_R_X_ALUMNO':'mean',
        }
    elif notas_group == 'B0':
        
        dic_valores = {
         'NOTA_C_X_ALUMNO' : np.where(df_notas_f['DA']=='C',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_M_X_ALUMNO' : np.where(df_notas_f['DA']=='M',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_F_X_ALUMNO' : np.where(df_notas_f['DA']=='F',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_R_X_ALUMNO' : np.where(df_notas_f['DA']=='R',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         
         'NOTA_P_X_ALUMNO' : np.where(df_notas_f['DA']=='P',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_T_X_ALUMNO' : np.where(df_notas_f['DA']=='T',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_Y_X_ALUMNO' : np.where(df_notas_f['DA']=='Y',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_S_X_ALUMNO' : np.where(df_notas_f['DA']=='S',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_L_X_ALUMNO' : np.where(df_notas_f['DA']=='L',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
        } 
        agg_config = {
         'NOTA_C_X_ALUMNO':'mean',
         'NOTA_M_X_ALUMNO':'mean', 
         'NOTA_F_X_ALUMNO':'mean',
         'NOTA_R_X_ALUMNO':'mean',
         
         'NOTA_P_X_ALUMNO':'mean',
         'NOTA_T_X_ALUMNO':'mean',
         'NOTA_Y_X_ALUMNO':'mean',
         'NOTA_S_X_ALUMNO':'mean',
         'NOTA_L_X_ALUMNO':'mean',
        }
    elif notas_group == 'F0':
        
        dic_valores = {
         'NOTA_C_X_ALUMNO' : np.where(df_notas_f['DA']=='C',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_M_X_ALUMNO' : np.where(df_notas_f['DA']=='M',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_F_X_ALUMNO' : np.where(df_notas_f['DA']=='F',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_R_X_ALUMNO' : np.where(df_notas_f['DA']=='R',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         
         'NOTA_E_X_ALUMNO' : np.where(df_notas_f['DA']=='E',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_D_X_ALUMNO' : np.where(df_notas_f['DA']=='D',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_G_X_ALUMNO' : np.where(df_notas_f['DA']=='G',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_I_X_ALUMNO' : np.where(df_notas_f['DA']=='I',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_A_X_ALUMNO' : np.where(df_notas_f['DA']=='A',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_H_X_ALUMNO' : np.where(df_notas_f['DA']=='H',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_B_X_ALUMNO' : np.where(df_notas_f['DA']=='B',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  , 
        } 
        agg_config = {
         'NOTA_C_X_ALUMNO':'mean',
         'NOTA_M_X_ALUMNO':'mean', 
         'NOTA_F_X_ALUMNO':'mean',
         'NOTA_R_X_ALUMNO':'mean',
         
         'NOTA_E_X_ALUMNO':'mean',
         'NOTA_D_X_ALUMNO':'mean',
         'NOTA_G_X_ALUMNO':'mean',
         'NOTA_I_X_ALUMNO':'mean',
         'NOTA_A_X_ALUMNO':'mean',
         'NOTA_H_X_ALUMNO':'mean',
         'NOTA_B_X_ALUMNO':'mean',
        }
    else:
        dic_valores = {
         'NOTA_C_X_ALUMNO' : np.where(df_notas_f['DA']=='C',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_M_X_ALUMNO' : np.where(df_notas_f['DA']=='M',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_P_X_ALUMNO' : np.where(df_notas_f['DA']=='P',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_T_X_ALUMNO' : np.where(df_notas_f['DA']=='T',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_Y_X_ALUMNO' : np.where(df_notas_f['DA']=='Y',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_F_X_ALUMNO' : np.where(df_notas_f['DA']=='F',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_R_X_ALUMNO' : np.where(df_notas_f['DA']=='R',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_S_X_ALUMNO' : np.where(df_notas_f['DA']=='S',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_L_X_ALUMNO' : np.where(df_notas_f['DA']=='L',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_E_X_ALUMNO' : np.where(df_notas_f['DA']=='E',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_D_X_ALUMNO' : np.where(df_notas_f['DA']=='D',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_G_X_ALUMNO' : np.where(df_notas_f['DA']=='G',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_I_X_ALUMNO' : np.where(df_notas_f['DA']=='I',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_A_X_ALUMNO' : np.where(df_notas_f['DA']=='A',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_H_X_ALUMNO' : np.where(df_notas_f['DA']=='H',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         'NOTA_B_X_ALUMNO' : np.where(df_notas_f['DA']=='B',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,    
         'NOTA_O_X_ALUMNO' : np.where(df_notas_f['DA']=='O',  df_notas_f['NOTA_AREA_REGULAR'],np.NaN)  ,
         
            
        }
        
        agg_config = {
         'NOTA_C_X_ALUMNO':'mean',
         'NOTA_M_X_ALUMNO':'mean',  
         'NOTA_P_X_ALUMNO':'mean', 
         'NOTA_T_X_ALUMNO':'mean',
         'NOTA_Y_X_ALUMNO':'mean',
         'NOTA_F_X_ALUMNO':'mean',
         'NOTA_R_X_ALUMNO':'mean',
         'NOTA_S_X_ALUMNO':'mean',
         'NOTA_L_X_ALUMNO':'mean',
         
         'NOTA_E_X_ALUMNO':'mean',
         'NOTA_D_X_ALUMNO':'mean',
         'NOTA_G_X_ALUMNO':'mean',
         'NOTA_I_X_ALUMNO':'mean',
         'NOTA_A_X_ALUMNO':'mean',
         'NOTA_H_X_ALUMNO':'mean',
         'NOTA_B_X_ALUMNO':'mean',
         
         'NOTA_O_X_ALUMNO':'mean',         

        }
        
    if "AGG_NOTA_ALUM" in cls_group:
        dic_valores['TOTAL_CURSOS_X_ALUMNO']=1
        dic_valores['TOTAL_CURSOS_VALIDOS_X_ALUMNO']=np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),1,0)
        dic_valores['TOTAL_CURSOS_APROBADOS_X_ALUMNO']=np.where((df_notas_f['NOTA_AREA_REGULAR']>=11),1,0) 
        dic_valores['MEAN_CURSOS_X_ALUMNO']=np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),df_notas_f['NOTA_AREA_REGULAR'],0)
        dic_valores['STD_CURSOS_X_ALUMNO']=np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),df_notas_f['NOTA_AREA_REGULAR'],0)  
        
        agg_config['TOTAL_CURSOS_X_ALUMNO']='sum'
        agg_config['TOTAL_CURSOS_VALIDOS_X_ALUMNO']='sum'
        agg_config['TOTAL_CURSOS_APROBADOS_X_ALUMNO']='sum'
        agg_config['MEAN_CURSOS_X_ALUMNO']='mean'
        agg_config['STD_CURSOS_X_ALUMNO']='std'
        
  
    dataSet_por_alumno = df_notas_f.assign(
     **dic_valores        
    ).groupby(['COD_MOD','ANEXO','ID_PERSONA']).agg(agg_config)
    

    return dataSet_por_alumno



def get_list_area_letter(notas_group):
    if notas_group== "CM":
        return ['C','M']
    elif notas_group== "COMMON":
        return ['C','M','F','R']
    elif notas_group== "B0":
        return ['C','M','P','T','Y','F','R', 'S','L']
    elif notas_group== "F0":
        return ['C','M','F','R', 'E','D','G', 'I','A', 'H','B']
    elif notas_group== "FULL":
        return ['C','M','P','T','Y','F','R', 'S','L', 'E','D','G', 'I','A', 'H','B', 'O']


def get_NC(area,postfix=None):
    if postfix is None :
        return 'NOTA_{}_X_ALUMNO'.format(area)
    else:
        return 'NOTA_{}_X_ALUMNO_{}'.format(area,postfix)

def get_ZN_I(area,postfix=None):
    return 'IMP_Z_NOTA_{}_{}'.format(area,postfix)

def get_ZN(area,postfix=None):
    return 'Z_NOTA_{}_{}'.format(area,postfix)

def get_MN(area,postfix=None):
    if postfix is None :
        return 'MEAN_NOTA_{}_X_CODMOD_NVL_GR'.format(area)
    else:
        return 'MEAN_NOTA_{}_X_CODMOD_NVL_GR_{}'.format(area,postfix)

def get_SN(area,postfix=None):
    if postfix is None :
        return 'STD_NOTA_{}_X_CODMOD_NVL_GR'.format(area)
    else:
        return 'STD_NOTA_{}_X_CODMOD_NVL_GR_{}'.format(area,postfix)


def existe_columna(df,cl):
    if cl not in  df:
        raise Exception("No se puede formatear la columna " + cl + ", no existe en el DF")
        
def formatear_TIENE_TRABAJO(df,drop=True):
    existe_columna(df,'HORAS_SEMANALES_TRABAJO') 
    existe_columna(df,'TRABAJA') 
    df['TIENE_TRABAJO'] = np.where((df.TRABAJA==1) | (df.HORAS_SEMANALES_TRABAJO>0) , 1 , 0 )
    print("NEW : {}".format('TIENE_TRABAJO'))
    if(drop):        
        df.drop(['TRABAJA','HORAS_SEMANALES_TRABAJO'], axis = 1,inplace=True) 
        print("drop : {}".format('TRABAJA'))
        print("drop : {}".format('HORAS_SEMANALES_TRABAJO'))
    

def formatear_TIENE_PADRES_COMO_APODERADO(df,drop=True):
    existe_columna(df,'PARENTESCO') 
    df['TIENE_PADRES_COMO_APODERADO'] = np.where((df.PARENTESCO=="MADRE") | (df.PARENTESCO=="PADRE") , 1 , 0 )
    print("NEW : {}".format('TIENE_PADRES_COMO_APODERADO'))
    if drop:
        df.drop(['PARENTESCO'], axis = 1,inplace=True) 
        print("drop : {}".format('PARENTESCO'))

def formatear_NO_VIVE_ALGUN_PADRE(df,drop=True):
    
    existe_columna(df,'PADRE_VIVE') 
    existe_columna(df,'MADRE_VIVE') 
    
    df['NO_VIVE_ALGUN_PADRE'] = np.where((df.PADRE_VIVE=="NO") | (df.MADRE_VIVE=="NO") , 1 , 0 )
    print("NEW : {}".format('NO_VIVE_ALGUN_PADRE'))
    if drop:
        df.drop(['PADRE_VIVE','MADRE_VIVE'], axis = 1,inplace=True) 
        print("drop : {}".format('PADRE_VIVE'))
        print("drop : {}".format('MADRE_VIVE'))

def formatear_TIENE_DISCAPACIDAD(df,drop=True):
    existe_columna(df,'TIENE_CERTIFICADO_DISCAPACIDAD') 
    existe_columna(df,'DSC_DISCAPACIDAD')
     
    df['TIENE_DISCAPACIDAD'] = np.where((df.DSC_DISCAPACIDAD!=0) | (df.TIENE_CERTIFICADO_DISCAPACIDAD=="SI") , 1 , 0 )
    print("NEW : {}".format('TIENE_DISCAPACIDAD'))
    if drop:
        df.drop(['DSC_DISCAPACIDAD','TIENE_CERTIFICADO_DISCAPACIDAD'], axis = 1,inplace=True) 
        print("drop : {}".format('DSC_DISCAPACIDAD'))
        print("drop : {}".format('TIENE_CERTIFICADO_DISCAPACIDAD'))

def formatear_TIENE_DNI(df,drop=True):
    existe_columna(df,'N_DOC')
    df['TIENE_DNI'] = np.where(df.N_DOC==0 , 0 , 1 )
    if(drop):
        df.drop(['N_DOC'], axis = 1,inplace=True)  
        print("drop : {}".format('N_DOC'))
    
    
    #df.drop(['EDAD_EN_DIAS_T','EDAD'], axis = 1,inplace=True)  

'''deprecated: la edad ya vendra en decimales, no sera necesario esta funcion
def formatear_dias_decimales(df):
    existe_columna(df,'EDAD_EN_DIAS_T')
    df['EDAD_EN_DECIMALES_T'] = df.EDAD_EN_DIAS_T/365.25
    df['EDAD_EN_DECIMALES_T'] = df.EDAD_EN_DECIMALES_T.round(2)
    
    if 'EDAD' in df:
        df.drop(['EDAD'], axis = 1,inplace=True)  
    if 'EDAD_EN_DIAS_T' in df:
        df.drop(['EDAD_EN_DIAS_T'], axis = 1,inplace=True)  
'''
        
def formatear_ES_MUJER(df,drop=True):
    existe_columna(df,'SEXO')
    df['ES_MUJER'] = np.where(df.SEXO=="MUJER" , 1 , 0 )
    print("NEW : {}".format('ES_MUJER'))
    if(drop):
        df.drop(['SEXO'], axis = 1,inplace=True)  
        print("drop : {}".format('SEXO'))
    
def formatear_ES_MUJER_APOD(df,drop=True):
    existe_columna(df,'SEXO_APOD')
    df['ES_MUJER_APOD'] = np.where(df.SEXO_APOD=="MUJER" , 1 , 0 )
    print("NEW : {}".format('ES_MUJER_APOD'))
    if(drop):
        df.drop(['SEXO_APOD'], axis = 1,inplace=True) 
        print("drop : {}".format('SEXO_APOD'))

def formatear_lengua_nacionalidad(df,drop=True):
    existe_columna(df,'DSC_LENGUA')
    existe_columna(df,'DSC_PAIS')
    df['ES_LENGUA_CASTELLANA'] = np.where(df.DSC_LENGUA=="CASTELLANO" , 1 , 0 )
    df['ES_PERUANO'] = np.where(df.DSC_PAIS.str.startswith('Per', na=False) , 1 , 0 )  
    
    print("NEW : {}".format('ES_LENGUA_CASTELLANA'))
    print("NEW : {}".format('ES_PERUANO'))
    
    if(drop):
        df.drop(['DSC_LENGUA','DSC_PAIS'], axis = 1,inplace=True) 
        print("drop : {}".format('DSC_LENGUA'))
        print("drop : {}".format('DSC_PAIS'))
    
    
def formatear_anio_escolaridad(df,drop=True):   
    anios_esc = {  'NINGUNO':0,              
                   'OTRO':0,
                   'PRIMARIA INCOMPLETA':4,
                   'PRIMARIA COMPLETA':6,
                   'SECUNDARIA INCOMPLETA':9,
                   'SECUNDARIA COMPLETA':11,
                   'SUPERIOR NO UNIV.INCOMPLETA':14,
                   'SUPERIOR NO UNIV.COMPLETA':16,
                   'SUPERIOR UNIV.INCOMPLETA':14,
                   'SUPERIOR UNIV.COMPLETA':16,
                   'SUPERIOR POST GRADUADO':20
                  }
    
    df['ANIOS_ESCOLARIDAD_APOD'] = df['NIVEL_INSTRUCCION_APOD'].map(anios_esc)
    print("NEW : {}".format('ANIOS_ESCOLARIDAD_APOD'))
    if(drop):
        df.drop(['NIVEL_INSTRUCCION_APOD'], axis = 1,inplace=True) 
        print("drop : {}".format('NIVEL_INSTRUCCION_APOD'))


def formatear_columnas_siaguie(df):
    
    formatear_anio_escolaridad(df)
    #formatear_dias_decimales(df)   
    formatear_ES_MUJER(df)    
    formatear_ES_MUJER_APOD(df)    
    formatear_lengua_nacionalidad(df)    
    formatear_TIENE_DNI(df)    
    formatear_TIENE_DISCAPACIDAD(df)    
    formatear_NO_VIVE_ALGUN_PADRE(df)    
    formatear_TIENE_PADRES_COMO_APODERADO(df)  
    formatear_TIENE_TRABAJO(df)  
    
    return df

'''  
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
url = hg.get_base_path()+"\\src\\Prj_Interrupcion_Estudios\\Prj_Desercion\\_02_Preparacion_Datos\\_02_Estructura_Base\\_data_\\nominal\\estructura_base_EBR_{}_{}_delta_1.csv"
url = url.format(5,2017)
df =pd.read_csv(url, dtype=dtypes_columns ,encoding="utf-8")

df=formatear_columnas_siaguie(df)

print(df.shape)
df_ = generar_kpis_desercion(df,anio_df=2019,anio_h=2018,t_anios=4)
print(df_.shape)



cls_json = {}
cls_json['SITUACION_FINAL']=["APROBADO","DESAPROBADO"]
#cls_json['SF_RECUPERACION']=["APROBADO","DESAPROBADO"]
#cls_json['SITUACION_MATRICULA']=["PROMOVIDO","REPITE","INGRESANTE","REENTRANTE"]
cls_json['JUNTOS']="dummy"
df_h = generar_kpis_historicos(df,anio_df=2017,anio_h=2016,cls_json=cls_json,t_anios=0 )
'''


