# -*- coding: utf-8 -*-
"""
Created on Fri Apr  9 00:36:06 2021

@author: User
"""
import pandas as pd
import numpy as np
from functools import reduce
#import core_helper.helper_acces_db as hadb

#import core_helper.helper_acces_db as hadb
#import core_helper.helper_clean as hc
#import core_helper.helper_general as hg
#import core_helper.helper_output as ho

import med_data_science_helper.helper_acces_db as hadb
import med_data_science_helper.helper_siagie_kpi as hsk

import data_science_helper.helper_clean as hc
import data_science_helper.helper_general as hg
import data_science_helper.helper_output as ho
import data_science_helper.helper_cache as hch

#df_siagie = hadb.get_siagie_por_anio(2022,columns_n= ['ID_PERSONA'])
#df_siagie2 = agregar_pivot_juntos(df_siagie, anio_df=2022,anio_h=2021,t_anios=3,cache=True)

def agregar_pivot_juntos(df,anio_df=None, anio_h=None , t_anios=1,delete_juntos_t_vcc=False, cache=False):
    

    ho.print_message('agregar_pivot_juntos')
    
    filename = 'agregar_pivot_juntos'
    key_cache = hch.get_key_cache([anio_df,anio_h,t_anios])
    print(key_cache)
    if cache:
        df_pivot = hch.get_cache(filename,key_cache)
        if df_pivot is not None:
            ho.print_items(df_pivot.columns,excepto=["DNI_MO"])
            if df is None:
                return 
            else:   
                #df = pd.merge(df,df_pivot, left_on=['DNI_MO','ANEXO'],right_on=['COD_MOD','ANEXO'], how='left')  
                df = pd.merge(df,df_pivot, left_on=['ID_PERSONA'],right_on=['ID_PERSONA'], how='inner') 
                #df['JUNTOS'] = np.where(df['DNI_MO'].isna(), 1, 0) 
                return df  
    
    
    
    ultimo_anio, num = hsk.gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios) 
    ultimo_anio_data = ultimo_anio + 1 
    if(ultimo_anio_data<2014):            
        msg = "ERROR: Se pretende consultar hasta el anio "+str(ultimo_anio_data)+", solo se tiene data hasta el 2016"     
        raise Exception(msg) 
        
    df_id_persona = hadb.get_siagie_por_anio(anio_df,columns_n= ['ID_PERSONA',"NUMERO_DOCUMENTO"])
          

      
    list_df=[]    
    for anio in range(anio_h,ultimo_anio,-1):
  
        if(anio<=2013):
            break        
  
        col_name="JUNTOS_T"
        col_VCC_name="VCC_{}_T"       

        if(num>0):
            posfix="_MENOS_{}".format(num)
            posfix_VCC="_MENOS_{}".format(num)            
            col_name = col_name+posfix
            col_VCC_name = col_VCC_name+posfix_VCC

        df_pv , periodos  = hadb.get_pivot_juntos(anio)
        print(anio)
        print(periodos)
        df_TMP = pd.merge(df_id_persona, df_pv ,left_on="NUMERO_DOCUMENTO", right_on="DNI_MO", how='left')
        
        df_TMP.drop("DNI_MO", axis = 1,inplace=True) 
        df_TMP.drop("NUMERO_DOCUMENTO", axis = 1,inplace=True) 
        
        df_TMP.fillna({'JUNTOS':0}, inplace=True)
        df_TMP.rename(columns={'JUNTOS': col_name}, inplace=True)
        
        lt_cl_vcc_delete = []
        for p in periodos:
            cl_vcc = 'VCC_{}'.format(p) 
            if col_name == "JUNTOS_T" and delete_juntos_t_vcc:     
                lt_cl_vcc_delete.append(cl_vcc)                
            else: 
                df_TMP.rename(columns={cl_vcc: col_VCC_name.format(p)}, inplace=True)
        
        if (len(lt_cl_vcc_delete)>0):
            df_TMP.drop(columns=lt_cl_vcc_delete, inplace=True)
        
        list_df.append(df_TMP)
        num+=1

    df_final_total = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df)
   

    ho.print_items(df_final_total.columns)
    hch.save_cache(df_final_total,filename,key_cache)
    
    
    if df is None:
        return 
    else:      

        df = pd.merge(df,df_final_total, left_on=['ID_PERSONA'],right_on=['ID_PERSONA'], how='left')          
        return df


def agregar_Censo_Educativo(df,df_ce=None,anio=2019, cache=False ):    
    
    ho.print_message('agregar_Censo_Educativo')
    if df_ce is None:
        df_ce = hadb.get_Censo_Educativo(anio=anio,cache=cache) 
    
    if 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    if 'ANEXO' not in df.columns:
        msg = "ERROR: No existe la columnna ANEXO en el DF proporcionado"
        raise Exception(msg)
        
    ho.print_items(df_ce.columns,excepto=['COD_MOD',"ANEXO"])
    
    if df is None:
        return 
    else:   
        df = pd.merge(df, df_ce, left_on=['COD_MOD',"ANEXO"], right_on=['COD_MOD',"ANEXO"],  how='left')    
        return df


def agregar_ECE(df,df_ece=None,anio=2019, cache=False ):    
    
    ho.print_message('agregar_ECE')
    if df_ece is None:
        df_ece = hadb.get_ECE(anio=anio,cache=cache) 
    
    if 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    ho.print_items(df_ece.columns,excepto=['COD_MOD',"ANEXO"])   
    
    if df is None:
        return 
    else:   
        df = pd.merge(df, df_ece, left_on=['COD_MOD',"ANEXO"], right_on=['COD_MOD',"ANEXO"],  how='left')
        return df


def agregar_nexus(df,anio_df=None,df_nexus=None,anio_h=2020, cache=False ):    
    
    ultimo_anio, num = hsk.gestionar_errores_filtro_kpi(anio_df,anio_h,1) 
    
    ho.print_message('agregar_nexus')
    if df_nexus is None:
        df_nexus = hadb.get_nexus(anio=anio_h,cache=cache) 
        
    posfix="_T"
    if num>0:
        posfix="_T_MENOS_{}".format(num)
    
    for col in df_nexus.columns:
        if (col!="COD_MOD"):
            col_posfix = col+posfix
            df_nexus.rename(columns={col: col_posfix}, inplace=True)
    
    if 'COD_MOD' not in df.columns:
        msg = "ERROR: No existe la columnna COD_MOD en el DF proporcionado"
        raise Exception(msg)
        
    ho.print_items(df_nexus.columns,excepto=["COD_MOD"])
        
    if df is None:
        return 
    else:   
        df = pd.merge(df, df_nexus, left_on=["COD_MOD"], right_on=["COD_MOD"],  how='left')    
        return df

def agregar_sisfoh(df,df_sisfoh=None, cache=False ):    
    
    ho.print_message('agregar_sisfoh')
    if cache:
        print("la cache para agregar_sisfoh no es necesario")
    if df_sisfoh is None:
        df_sisfoh = hadb.get_sisfoh()  
    
    if 'NUMERO_DOCUMENTO_APOD' not in df.columns:
        msg = "ERROR: No existe la columnna NUMERO_DOCUMENTO_APOD en el DF proporcionado"
        raise Exception(msg)
        
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].str.replace('.0', '')
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].apply(lambda x: '{0:0>8}'.format(x))
    df['NUMERO_DOCUMENTO_APOD'] = df['NUMERO_DOCUMENTO_APOD'].str.replace('00000nan', '00000000')     
    
    ho.print_items(df_sisfoh.columns,excepto=["PERSONA_NRO_DOC"])
    
    if df is None:
        return 
    else:  
        df = pd.merge(df, df_sisfoh, left_on=["NUMERO_DOCUMENTO_APOD"], right_on=["PERSONA_NRO_DOC"],  how='left')   
        df = hc.fill_nan_with_nan_category_in_cls(df , ["SISFOH_CSE"])
        del df["PERSONA_NRO_DOC"]        
        return df

# solo disponible 2019 y 2021 (EBE,) , 2020 (A0, B0 , F0, EBE). 
def agregar_shock_economico(df,df_se=None,anio=None,modalidad="EBR", cache=False ):
    
    ho.print_message('agregar_shock_economico')

    if df_se is None:
        df_se = hadb.get_shock_economico(anio,cache=cache)
    
    #print("hola")
    ho.print_items(df_se.columns)

    if df is None:
        return 
    else:  
        
        df = pd.merge(df, df_se, left_on="ID_PERSONA", right_on="ID_PERSONA",  how='inner')
        return df

