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
#import core_helper.helper_clean as hc


import med_data_science_helper.helper_acces_db as hadb
from data_science_helper import helper_dataframe as hdf
import data_science_helper.helper_general as hg
import data_science_helper.helper_clean as hc

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


def generar_kpis_traslado(df,anio_df=None , anio_h =None ,t_anios=None,modalidad="EBR"):
    
    ID_PERSONA_SERIES = df['ID_PERSONA']
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
    print()
    df_final.drop(cols_to_drop, axis = 1,inplace=True)    
    print(cols_to_sum)
    df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
    
    return df

def generar_kpis_traslado_a_publico(df,anio_df=None, anio_h =None ,t_anios=None,df_servicios=None,modalidad="EBR"):
    
    if df_servicios is None:
        df_servicios = hadb.get_df_servicios()
    
    ID_PERSONA_SERIES = df['ID_PERSONA']
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
    
    df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
    
    return df


def generar_kpis_desercion(df,anio_df=None, anio_h=None ,t_anios=None,modalidad="EBR"):
        
    ID_PERSONA_SERIES = df['ID_PERSONA']
    ultimo_anio, num = gestionar_errores_filtro_kpi(anio_df,anio_h,t_anios)
    #ultimo_anio =ANIO- T_ANIOS       
    #num = 1
    list_df_m_tras = []
    cols_to_sum = []
    cols_to_drop = []
    #ANIO = ANIO-1
    print("anio_h : ",anio_h," ultimo_anio : ",ultimo_anio)
    for anio in range(anio_h,ultimo_anio,-1):
        print("anio : ",anio)
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
    
    df = pd.merge(df, df_final, left_on=["ID_PERSONA"],  right_on=["ID_PERSONA"],  how='inner')
    
    return df



def agregar_distancia_prim_sec(df):
    df_dist= hadb.get_distancia_prim_sec()
    df = pd.merge(df,df_dist, left_on=['COD_MOD','ANEXO'],right_on=['COD_MOD','ANEXO'], how='left')  
    return df




def generar_kpis_historicos(df,anio_df=None,anio_h=None,cls_json=None,t_anios=0,modalidad="EBR"):
    
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
        
    print(' '.join(cls_list)) 
    


    ID_PERSONA_SERIES = df['ID_PERSONA']
    

    num = anio_df-anio_h
    list_df_m_tras = []

    
    kpi_final_dic = {}
    print()
    for anio in range(anio_h,ultimo_anio,-1):
        if(anio<=2013):
            break

        print("ANIO =================>>>>>>>>>  : ",anio)
        df_m_t = pd.merge(ID_PERSONA_SERIES, hadb.get_siagie_por_anio(anio,modalidad=modalidad,columns_n=cls_list),left_on="ID_PERSONA",
                          right_on="ID_PERSONA", how='left')
        
        df_m_t.fillna("NaN",inplace=True)
        
        df_m_t = hc.trim_category_cls(df_m_t)
        
        for key, values in cls_json.items():
            if  isinstance(values, list):
         
                print("------------------category---------------------")
                for val in values:
                    key_val = key+"_"+val
                    if num ==0:
                        cl_pf = key_val+"_T"               
                    else:
                        cl_pf = key_val+"_T_MENOS_{}".format(num)  
                        
                    df_m_t[cl_pf] = np.NaN 
                    df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==val), cl_pf] = 1
                    df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]!=val), cl_pf] = 0                 
                                   
                    print(cl_pf)
                    if  (key_val in kpi_final_dic) ==False:
                        kpi_final_dic[key_val]=[]                    
                    kpi_final_dic[key_val].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 
            elif values=="dummy":      
                
                print("-----------------dummy----------------------")
                if num ==0:
                    cl_pf = key+"_T"              
                else:
                    cl_pf = key+"_T_MENOS_{}".format(num)                
                #df_m_t[cl_pf] = np.where((df_m_t[key]==1),1,0)
                
                df_m_t[cl_pf] = np.NaN 
                df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==1), cl_pf] = 1
                df_m_t.loc[(df_m_t[key]!="NaN") & (df_m_t[key]==0), cl_pf] = 0    
                
                print(cl_pf)
                
                if  (key in kpi_final_dic) ==False:
                    kpi_final_dic[key]=[]                    
                kpi_final_dic[key].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 
                
            elif values=="numero":    
                
                print("-----------------numero----------------------")                
                if num ==0:
                    cl_pf = key+"_T"              
                else:
                    cl_pf = key+"_T_MENOS_{}".format(num)    
                    
                df_m_t[cl_pf] = np.NaN    
                df_m_t.loc[(df_m_t[key]!="NaN"), cl_pf] = df_m_t[key] 
                
                #df_m_t[cl_pf] = df_m_t[key]  
                print(cl_pf)
                if  (key in kpi_final_dic) ==False:
                    kpi_final_dic[key]=[]                    
                kpi_final_dic[key].append(cl_pf)
                df_m_t.drop([key], axis = 1,inplace=True) 

        list_df_m_tras.append(df_m_t)
        num+=1

    df_final = reduce(lambda left,right: pd.merge(left,right,on='ID_PERSONA'), list_df_m_tras)


    kpi_list = []
    for key, cls_anios in kpi_final_dic.items():
        kpi_list.append(key)   
        df_final = set_generic_kpis(df_final,key,cls_anios)
        #df_final.drop(cls_anios, axis = 1,inplace=True) 
     
    df_final = pd.merge(df , df_final, left_on=['ID_PERSONA'], right_on=['ID_PERSONA'], how='inner',suffixes=('','_repetido'))    
     
    return df_final


def set_generic_kpis(df,cl_name=None,cl_list=[],set_nan=False):

    if(set_nan==False):
        if(len(cl_list)>1):            
            print("---------------------------------------") 
            t_cl_name = 'TOTAL_'+cl_name
            df[t_cl_name] = df[cl_list].sum(axis=1)
            print(t_cl_name)
            
            m_cl_name = 'MEAN_'+cl_name
            df[m_cl_name] = df[cl_list].mean(axis=1)
            print(m_cl_name)
            
            if(len(cl_list)>2):
                st_cl_name = 'STD_'+cl_name 
                df[st_cl_name] = df[cl_list].std(axis=1)
                print(st_cl_name)
                
            mi_cl_name = 'MIN_'+cl_name    
            df[mi_cl_name] = df[cl_list].min(axis=1)
            print(mi_cl_name)
            
            ma_cl_name = 'MAX_'+cl_name  
            df[ma_cl_name] = df[cl_list].max(axis=1)
            print(ma_cl_name)
    else:
        df['TOTAL_'+cl_name] = np.nan
        df['MEAN_'+cl_name] = np.nan
        df['STD_'+cl_name] = np.nan
    return df



def agregar_notas(df,anio_df=None,anio_notas=None,df_notas=None,
                  min_alumn_zscore=20,
                  cls_group=["NOTA","ZSCORE","AGG_CODMOD_GR","AGG_NOTA_ALUM"]):

    if df is None:
        msg = "ERROR: Debe proporcionar el DF de alumnos"
        raise Exception(msg)
        #return
    
    if 'ID_PERSONA' not in df.columns:
        msg = "ERROR: El dataframe df no tiene la columna ID_PERSONA"
        raise Exception(msg)
    
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
    print("postfix : ",postfix)
    print("---------df_notas------------")
    #print(df_notas.dtypes)
    print(df_notas.shape)

    #df_notas = get_df_notas(anio)
    
    #notas del anio n_menos_1 de los alumnos del anio n
    df_notas_f = pd.merge(df_notas , df['ID_PERSONA'], left_on='ID_PERSONA', 
                          right_on='ID_PERSONA', how='inner')
    
    print("---------df_notas_f------------")
    #print(df_notas_f.dtypes)
    print(df_notas_f.shape)
    
    print("Total notas inicial : ",df_notas_f.shape)
    df_ser=df_notas_f.groupby(['COD_MOD', 'ANEXO']).size().reset_index()[['COD_MOD', 'ANEXO']]
    #hay que optener el listado total de alumnos del anio pasado para hacer los group_by respectivos con la data total de n-1.
    #estos alumnos deben pertenecer a los mismos servicios que los alumnos del anio n
    df_notas_alum_n_mes_1 = pd.merge(df_notas , df_ser, left_on=['COD_MOD','ANEXO'], 
                          right_on=['COD_MOD','ANEXO'], how='inner')
    
    df_notas_alum_n_mes_1 = hdf.reduce_mem_usage(df_notas_alum_n_mes_1)
    df_notas_f = hdf.reduce_mem_usage(df_notas_f)
    
    print("---------df_notas_f------------")
    #print(df_notas_f.dtypes)
    print(df_notas_f.shape)
    
    print("---------df_notas_alum_n_mes_1------------")
    #print(df_notas_alum_n_mes_1.dtypes)
    print(df_notas_alum_n_mes_1.shape)
    

    df_alum_nota = get_df_final_notas_alumn(df_notas_f,df_notas_alum_n_mes_1,postfix,min_alumn_zscore)
    print("---------df_alum_nota------------")
    #print(df_alum_nota.dtypes)
    print(df_alum_nota.shape)
    df_alum_nota = hdf.reduce_mem_usage(df_alum_nota)
    #print(df_alum_nota.dtypes)
    print(df_alum_nota.shape)
    
    #column_j_alum_not = ['COD_MOD','ANEXO','ID_PERSONA']  
    column_j_alum_not = ['ID_PERSONA']   
    
    list_area_letter = get_list_area_letter()
    for a_l in list_area_letter:       
        df_alum_nota.rename(columns={get_NC(a_l): get_NC(a_l,postfix)}, inplace=True)
        df_alum_nota.rename(columns={get_MN(a_l): get_MN(a_l,postfix)}, inplace=True)
        df_alum_nota.rename(columns={get_SN(a_l): get_SN(a_l,postfix)}, inplace=True)
        
    df_alum_nota.rename(columns={'TOTAL_CURSOS_X_ALUMNO': 'TOTAL_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'TOTAL_CURSOS_VALIDOS_X_ALUMNO': 'TOTAL_CURSOS_VALIDOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'TOTAL_CURSOS_APROBADOS_X_ALUMNO': 'TOTAL_CURSOS_APROBADOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'MEAN_CURSOS_X_ALUMNO': 'MEAN_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
    df_alum_nota.rename(columns={'STD_CURSOS_X_ALUMNO': 'STD_CURSOS_X_ALUMNO_'+postfix}, inplace=True)                  
          
    del df_alum_nota['TOTAL_ALUMNOS_X_CODMOD_NVL_GR']
    print("---------------------")
    #print(df.dtypes)
    #print("---------------------")
    #print(df_alum_nota.dtypes)
    #print("---------------------")
    
    #cls_group=["NOTA","ZSCORE","AGG_CODMOD_GR","AGG_NOTA_ALUM"]
    
    list_cls = []
    print("**********COLUMNAS GENERADAS****************")
    for group in cls_group:
        if group == "NOTA":
            sub_list = df_alum_nota.loc[:,df_alum_nota.columns.str.startswith('NOTA_')].columns
            print(sub_list)
            list_cls.append(sub_list)
            print("*******************************************************")
        if group == "ZSCORE":
            sub_list = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('Z_NOTA')].columns
            print(sub_list)
            list_cls.append(sub_list)
            print("********************************************************")
        if group == "AGG_CODMOD_GR":
            sub_list = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('CODMOD_NVL_GR')].columns  
            print(sub_list)
            list_cls.append(sub_list)
            print("*********************************************************")
        if group == "AGG_NOTA_ALUM":
            sub_list = df_alum_nota.loc[:,df_alum_nota.columns.str.contains('CURSOS')].columns
            print(sub_list)
            list_cls.append(sub_list)
            print("*********************************************************")
    list_cls = hg.flat_list(list_cls) 

    list_cls.append('ID_PERSONA')   
    
    df_join_model = pd.merge(df , df_alum_nota[list_cls], left_on=['ID_PERSONA'], 
                             right_on=column_j_alum_not, how='left',suffixes=('','_x'))
    
    #del df_join_model['COD_MOD_x']
    #del df_join_model['ANEXO_x']
    df_join_model = hdf.reduce_mem_usage(df_join_model)
    
    #creando dummy que indica si el zscore esta nullo o no
    list_area_letter = get_list_area_letter()
    for a_l in list_area_letter:
        hc.agregar_na_cls(df_join_model,get_ZN(a_l,postfix))
        

    #df_join_model.fillna(0,inplace=True)
    return df_join_model


def get_df_final_notas_alumn(df_notas_f,df_notas_alum_n_mes_1,postfix,min_alumn):
    #print(df_notas_f.dtypes)
    df_a = get_df_por_alum(df_notas_f)
    df_a.reset_index(inplace=True)
    df_a['COD_MOD']=df_a['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    df_a['ANEXO']=df_a['ANEXO'].astype('int')

    #dataSet_por_alumno.head()

    dataSet_por_nivel_grado_serv, dataSet_por_nivel_grado = get_df_por_grado_serv(df_notas_alum_n_mes_1)
    
    #print(dataSet_por_nivel_grado)
    
    dataSet_por_nivel_grado_serv.reset_index(inplace=True)
    dataSet_por_nivel_grado_serv['COD_MOD']=dataSet_por_nivel_grado_serv['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    dataSet_por_nivel_grado_serv['ANEXO']=dataSet_por_nivel_grado_serv['ANEXO'].astype('int')
    #dataSet_por_nivel_grado.head()
    #print(df_a.dtypes)
    print("**********************************")
    #print(dataSet_por_nivel_grado_serv.dtypes)

    #print("df_a 1>",df_a.shape)
    df_a = pd.merge(df_a, dataSet_por_nivel_grado_serv, left_on=["COD_MOD","ANEXO"],  right_on=["COD_MOD","ANEXO"],  how='inner')
    #print("df_a 2>",df_a.shape)
    
    list_area_letter = get_list_area_letter()

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
    df_notas_por_grado_serv =  get_df_notas_por_groupby(df_notas_f)
    df_notas_f['dummy']=1
    df_notas_por_grado =  get_df_notas_por_groupby(df_notas_f,groupby=['dummy'],agg_label='CODMOD_NVL_GR')
    
    return df_notas_por_grado_serv, df_notas_por_grado


def get_df_notas_por_groupby(df_notas_f,groupby=['COD_MOD','ANEXO'],agg_label='CODMOD_NVL_GR'):
    #print(df_notas_f.columns)
    dataSet_por_nivel_grado = df_notas_f.assign(   

    ############## mean ##############   
     #A3 A2 A5  B0 F0
     MEAN_NOTA_M_X_CODMOD_NVL_GR =  np.where(df_notas_f['DA']=='M', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN),  
        
     MEAN_NOTA_C_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='C',
                                            df_notas_f['NOTA_AREA_REGULAR'],np.NaN),
        
     MEAN_NOTA_V_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='V',
                                            df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     MEAN_NOTA_G_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='G',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_F_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='F',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     MEAN_NOTA_T_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='T',
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
           
     MEAN_NOTA_A_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='A',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_J_X_CODMOD_NVL_GR = np.where(df_notas_f['DA']=='J',
                                           df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     MEAN_NOTA_O_X_CODMOD_NVL_GR =   np.where((df_notas_f['DA']=='O') &                                                  
                                              (df_notas_f['NOTA_AREA_REGULAR']>=0),
                                               df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     ############## std ##############   
     #A3 A2 A5  B0 F0
     STD_NOTA_M_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='M', 
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_C_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='C',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_V_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='V',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

        
     STD_NOTA_G_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='G',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_F_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='F',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        

     STD_NOTA_T_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='T',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_A_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='A',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_J_X_CODMOD_NVL_GR =   np.where(df_notas_f['DA']=='J',
                                             df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     STD_NOTA_O_X_CODMOD_NVL_GR =   np.where((df_notas_f['DA']=='O') &                                              
                                                 (df_notas_f['NOTA_AREA_REGULAR']>=0),
                                                  df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
     
     TOTAL_ALUMNOS_X_CODMOD_NVL_GR = df_notas_f['ID_PERSONA']

    ).groupby(groupby).agg({
                                        'MEAN_NOTA_M_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_C_X_{}'.format(agg_label):'mean',  
                                        'MEAN_NOTA_V_X_{}'.format(agg_label):'mean', 
                                        'MEAN_NOTA_G_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_F_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_T_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_A_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_J_X_{}'.format(agg_label):'mean',
                                        'MEAN_NOTA_O_X_{}'.format(agg_label):'mean',
        
                                        'STD_NOTA_M_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_C_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_V_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_G_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_F_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_T_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_A_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_J_X_{}'.format(agg_label):'std',
                                        'STD_NOTA_O_X_{}'.format(agg_label):'std',      
                                        
                                        'TOTAL_ALUMNOS_X_{}'.format(agg_label):'nunique', 
                                       })
    
    #dataSet_por_nivel_grado['COD_MOD']=dataSet_por_nivel_grado['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    #dataSet_por_nivel_grado['ANEXO']=dataSet_por_nivel_grado['ANEXO'].astype('int')

    return dataSet_por_nivel_grado


def get_df_por_alum(df_notas_f):

    dataSet_por_alumno = df_notas_f.assign(

     NOTA_M_X_ALUMNO =  np.where(df_notas_f['DA']=='M', 
                                 df_notas_f['NOTA_AREA_REGULAR'],np.NaN),  
        
     NOTA_C_X_ALUMNO = np.where(df_notas_f['DA']=='C',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN),
        
     NOTA_V_X_ALUMNO = np.where(df_notas_f['DA']=='V',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     NOTA_G_X_ALUMNO = np.where(df_notas_f['DA']=='G',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     NOTA_F_X_ALUMNO = np.where(df_notas_f['DA']=='F',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     NOTA_T_X_ALUMNO = np.where(df_notas_f['DA']=='T',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
           
     NOTA_A_X_ALUMNO = np.where(df_notas_f['DA']=='A',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     NOTA_J_X_ALUMNO = np.where(df_notas_f['DA']=='J',
                                df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 
        
     NOTA_O_X_ALUMNO = np.where((df_notas_f['DA']=='O') &                                                  
                                (df_notas_f['NOTA_AREA_REGULAR']>=0),
                                 df_notas_f['NOTA_AREA_REGULAR'],np.NaN), 

     TOTAL_CURSOS_X_ALUMNO =   1, 
     TOTAL_CURSOS_VALIDOS_X_ALUMNO =   np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),1,0),      
     TOTAL_CURSOS_APROBADOS_X_ALUMNO =   np.where((df_notas_f['NOTA_AREA_REGULAR']>=11),1,0), 
     MEAN_CURSOS_X_ALUMNO =   np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),df_notas_f['NOTA_AREA_REGULAR'],0), 
     STD_CURSOS_X_ALUMNO =   np.where((df_notas_f['NOTA_AREA_REGULAR']>=0),df_notas_f['NOTA_AREA_REGULAR'],0),   
        
    ).groupby(['COD_MOD','ANEXO','ID_PERSONA']).agg({
                                                    'NOTA_M_X_ALUMNO':'mean',
                                                    'NOTA_C_X_ALUMNO':'mean',  
                                                    'NOTA_V_X_ALUMNO':'mean', 
                                                    'NOTA_G_X_ALUMNO':'mean',
                                                    'NOTA_F_X_ALUMNO':'mean',
                                                    'NOTA_T_X_ALUMNO':'mean',
                                                    'NOTA_A_X_ALUMNO':'mean',
                                                    'NOTA_J_X_ALUMNO':'mean',
                                                    'NOTA_O_X_ALUMNO':'mean',
                                                    
                                                    'TOTAL_CURSOS_X_ALUMNO':'sum',
                                                    'TOTAL_CURSOS_VALIDOS_X_ALUMNO':'sum',
                                                    'TOTAL_CURSOS_APROBADOS_X_ALUMNO':'sum',
                                                    
                                                    'MEAN_CURSOS_X_ALUMNO':'mean',
                                                    'STD_CURSOS_X_ALUMNO':'std',
                                                   })
    

    return dataSet_por_alumno



def get_list_area_letter():
    return ['M','C','V','G','F','T','A','J','O']

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
        
def formatear_TIENE_TRABAJO(df):
    existe_columna(df,'HORAS_SEMANALES_TRABAJO') 
    existe_columna(df,'TRABAJA') 
    df['TIENE_TRABAJO'] = np.where((df.TRABAJA==1) | (df.HORAS_SEMANALES_TRABAJO>0) , 1 , 0 )
    df.drop(['TRABAJA','HORAS_SEMANALES_TRABAJO'], axis = 1,inplace=True) 
    

def formatear_TIENE_PADRES_COMO_APODERADO(df):
    existe_columna(df,'PARENTESCO') 
    df['TIENE_PADRES_COMO_APODERADO'] = np.where((df.PARENTESCO=="MADRE") | (df.PARENTESCO=="PADRE") , 1 , 0 )
    df.drop(['PARENTESCO'], axis = 1,inplace=True) 

def formatear_NO_VIVE_ALGUN_PADRE(df):
    
    existe_columna(df,'PADRE_VIVE') 
    existe_columna(df,'MADRE_VIVE') 
    
    df['NO_VIVE_ALGUN_PADRE'] = np.where((df.PADRE_VIVE=="NO") | (df.MADRE_VIVE=="NO") , 1 , 0 )
    df.drop(['PADRE_VIVE','MADRE_VIVE'], axis = 1,inplace=True) 

def formatear_TIENE_DISCAPACIDAD(df):
    existe_columna(df,'TIENE_CERTIFICADO_DISCAPACIDAD') 
    existe_columna(df,'DSC_DISCAPACIDAD')
     
    df['TIENE_DISCAPACIDAD'] = np.where((df.DSC_DISCAPACIDAD!=0) | (df.TIENE_CERTIFICADO_DISCAPACIDAD=="SI") , 1 , 0 )
    df.drop(['DSC_DISCAPACIDAD','TIENE_CERTIFICADO_DISCAPACIDAD'], axis = 1,inplace=True) 

def formatear_TIENE_DNI(df):
    existe_columna(df,'N_DOC')
    df['TIENE_DNI'] = np.where(df.N_DOC==0 , 0 , 1 )
    #df.drop(['EDAD_EN_DIAS_T','EDAD'], axis = 1,inplace=True)  

def formatear_dias_decimales(df):
    existe_columna(df,'EDAD_EN_DIAS_T')
    df['EDAD_EN_DECIMALES_T'] = df.EDAD_EN_DIAS_T/365.25
    df['EDAD_EN_DECIMALES_T'] = df.EDAD_EN_DECIMALES_T.round(2)
    
    if 'EDAD' in df:
        df.drop(['EDAD'], axis = 1,inplace=True)  
    if 'EDAD_EN_DIAS_T' in df:
        df.drop(['EDAD_EN_DIAS_T'], axis = 1,inplace=True)  
        
def formatear_ES_MUJER(df):
    existe_columna(df,'SEXO')
    df['ES_MUJER'] = np.where(df.SEXO=="MUJER" , 1 , 0 )
    df.drop(['SEXO'], axis = 1,inplace=True)  
    
def formatear_ES_MUJER_APOD(df):
    existe_columna(df,'SEXO_APOD')
    df['ES_MUJER_APOD'] = np.where(df.SEXO_APOD=="MUJER" , 1 , 0 )
    df.drop(['SEXO_APOD'], axis = 1,inplace=True) 

def formatear_lengua_nacionalidad(df):
    existe_columna(df,'DSC_LENGUA')
    existe_columna(df,'DSC_PAIS')
    df['ES_LENGUA_CASTELLANA'] = np.where(df.DSC_LENGUA=="CASTELLANO" , 1 , 0 )
    df['ES_PERUANO'] = np.where(df.DSC_PAIS.str.startswith('Per', na=False) , 1 , 0 )    
    
    
def formatear_anio_escolaridad(df):   
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
    #return df


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


