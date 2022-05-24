# -*- coding: utf-8 -*-
import data_science_helper.helper_general as hg
#import core_helper.helper_general as hg
#hg.set_base_path()

#import src.Prj_Core.core_helper.model.general as g
import json
import pandas as pd
import numpy as np
import os.path as path
from pathlib import Path
import os
import ast
#import core_helper.helper_general as hg  
#import core_helper.helper_dataframe as hd
#import core_helper.helper_cache as hc

import data_science_helper.helper_dataframe as hd
import data_science_helper.helper_cache as hc

from simpledbf import Dbf5



MR_File_Name = "base.txt"

def set_macro_region(filename):
    global MR_File_Name
    MR_File_Name = filename

def get_macro_region(macro):
    global MR_File_Name
    js_mr = hg.get_base_path()+"/config/macro_region/"+MR_File_Name
    with open(js_mr) as json_file:
        data = json.load(json_file)        
        
    if macro not in data: 
            raise Exception("No existe la clave [ " + macro + " ] en el archivo: "+MR_File_Name)
        
    return data[macro]

def get_path_BD():
    try:
        path_config_file = hg.get_base_path()+"\\config\\config.txt"
        file = open(path_config_file, "r")
        contents = file.read()
        dictionary = ast.literal_eval(contents)
        dictionary["med-data-science-helper"]
    except:
        print("ERROR: Hay problemas en leer el archivo {}".format(path_config_file))
    
    path_file = dictionary["med-data-science-helper"]+"\\src"
    return path_file


def get_path_BD_siagie_procesado():
    path_file =get_path_BD() +"\\01.SIAGIE\\_data_\\procesado"
    return path_file

def get_path_BD_siagie_sin_procesar():
    path_file =get_path_BD() +"\\01.SIAGIE\\_data_\\sin_procesar"
    return path_file


def get_juntos(anio=2022,cache=False):  
    url_ = get_path_BD()+'\\13.Juntos\\_data_\\Educacion_{}.csv'.format(anio)   
    df_juntos = pd.read_csv(url_,dtype={'DNI_MO':"str"})
    df_juntos = df_juntos[df_juntos["TIPODOC_MO"]==1].copy()
    return df_juntos

def get_pivot_juntos(anio=2022,cache=False):

    df = get_juntos(anio=anio, cache=cache)
    
    periodos = df.PERIODO.unique()
    
    df['PERIODO'] = 'VCC_' + df['PERIODO'].astype(str)   
    
    #df_p = df.pivot_table(index=["ID_PERSONA_MO","TIPODOC_MO","DNI_MO","COTEJO_MO","ANIO"], values='RESULTADO_HOGAR', columns='PERIODO') \
      
    
    df_p = df.pivot_table(index=["DNI_MO"], values='RESULTADO_HOGAR', columns='PERIODO', aggfunc=np.max) \
        .reset_index() \
        .rename_axis(None, axis=1)
     
    df_p['JUNTOS'] = 1    
    #df_p.drop(columns=['ID_PERSONA_MO', 'ANIO'], inplace=True)
        
    return df_p , periodos



def get_agg_juntos(anio=2022,cache=False):
        
    df = get_juntos(anio=anio, cache=cache)
    
    df_ = df.groupby(["TIPODOC_MO",'DNI_MO'])[['RESULTADO_HOGAR']].agg('count').reset_index()   
        
    return df_

'''
url_template = get_path_BD()+'\\07.Nexus\\_data_\\{}'     
url_nexus = url_template.format('nexus_2018_2019.xlsb')    
anio = 2019
df_nexus = pd.read_excel(url_nexus, engine='pyxlsb',sheet_name=str(anio))   
print(df_nexus.columns)
print(df_nexus.SITUACION.value_counts()) 

SITUACION
'''
def get_nexus(anio=2020,subtipo_trabajador=["DOCENTE"], estado_plaza=["Activo","Encargatura"], cache=False):  

    if anio in [2015,2016,2017,2020,2021] :
        filename = 'nexus_2015_2016_2017_2020_2021.xlsb'
    elif anio in [2018,2019]:
        filename = 'nexus_2018_2019.xlsb'
    else :
        return None

    if(subtipo_trabajador is None):
        subtipo_trabajador = []
        
    if(estado_plaza is None):
        estado_plaza = []

    params = subtipo_trabajador+estado_plaza
    params_str = '_'.join(params)
    
    df_nexus_group = None
    key_cache = hc.get_key_cache([anio,params_str])
    print(key_cache)
    if cache:
        df_nexus_group = hc.get_cache(filename,key_cache)
        
    if df_nexus_group is not None:
        return df_nexus_group

    
    url_template = get_path_BD()+'\\07.Nexus\\_data_\\{}'     
    url_nexus = url_template.format(filename)    
    
    df_nexus = pd.read_excel(url_nexus, engine='pyxlsb',sheet_name=str(anio))       
    
#    if filename == "nexus_2015_2016_2017_2020_2021.xlsb":
#        df_nexus.rename(columns={"MODULAR IE": "codmod"},inplace=True)
        
    if filename == "nexus_2018_2019.xlsb":
        df_nexus.rename(columns={"SITUACION": "SITUACION LAB"},inplace=True)
        
    
    df_nexus['MODULAR IE'] = df_nexus['MODULAR IE'].str.strip()
    df_nexus['SITUACION LAB'] = df_nexus['SITUACION LAB'].str.strip()
    df_nexus['ESTADO PLAZA'] = df_nexus['ESTADO PLAZA'].str.strip()
    df_nexus['SUBTIPO TRABAJADOR'] = df_nexus['SUBTIPO TRABAJADOR'].str.strip()
    df_nexus['NIVEL EDUCATIVO'] = df_nexus['NIVEL EDUCATIVO'].str.strip()    

    df_nexus.rename(columns={"MODULAR IE": "codmod"},inplace=True)
    
    
    if(subtipo_trabajador is not None and len(subtipo_trabajador)>0):
        df_nexus = df_nexus[df_nexus["SUBTIPO TRABAJADOR"].isin(subtipo_trabajador)]
    
    if(estado_plaza is not None and len(estado_plaza)>0):
        df_nexus = df_nexus[df_nexus["ESTADO PLAZA"].isin(estado_plaza)]
            
    
    df_nexus['sitlab'] = df_nexus['SITUACION LAB'].astype(str).str[0]

    df_nexus['sitlab_2']='O'
    df_nexus.loc[(df_nexus['sitlab'] == "C"), 'sitlab_2'] = 'C'
    df_nexus.loc[(df_nexus['sitlab'] == "N"), 'sitlab_2'] = 'N'

    df_nexus.loc[(df_nexus['sitlab_2'] == "C"), 'C'] = 1
    df_nexus.loc[(df_nexus['sitlab_2'] == "N"), 'N'] = 1
    df_nexus.loc[(df_nexus['sitlab_2'] == "O"), 'O'] = 1

    df_nexus_group = df_nexus.groupby(['codmod'])[['C',"N",'O']].agg("sum").reset_index()
    df_nexus_group['tot_doc_nex'] = df_nexus_group[['C',"N",'O']].sum(axis=1)

    df_nexus_group['RATIO_CONT_X_CMOD']= df_nexus_group['C']/df_nexus_group['tot_doc_nex']
    df_nexus_group['RATIO_NOMB_X_CMOD']= df_nexus_group['N']/df_nexus_group['tot_doc_nex']
    df_nexus_group['RATIO_OT_X_CMOD']= df_nexus_group['O']/df_nexus_group['tot_doc_nex']

    df_nexus_group.drop_duplicates(subset=['codmod'], keep='last',inplace=True)

    df_nexus_group.rename(columns={"codmod": "COD_MOD"},inplace=True)
    
    df_nexus_group.drop(columns=['C','N','O','tot_doc_nex'],inplace=True)
    
    
    #df_nexus_group.to_hdf('cache.h5', key='df_nexus_codmod', mode='a')
    hc.save_cache(df_nexus_group,filename,key_cache)
    return df_nexus_group


def get_ECE_2P(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Primaria\\EM_2019_2P_alumnos.xlsx'  
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,O,Q",dtype={'cod_mod7':str,'anexo':'int8'})    
    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        df["COD_MOD"] =df['COD_MOD'].astype("str")
        df["ANEXO"] =df['ANEXO'].astype("int8")
        return df
    df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
    df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
    df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

    df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
    df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
    df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1

    df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l1',"grupo_l2",'grupo_l3',
                                                 'grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

    df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
    df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "2P"
    
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]


def get_ECE_4P(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Primaria\\EM_2019_4P_alumnos.xlsx'        
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,O,Q",dtype={'cod_mod7':str,'anexo':'int8'})     
        
        df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1
        
        df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l1',"grupo_l2",'grupo_l3',
                                                     'grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

        df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
        df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])
        
    elif  anio == 2018:
        url =   get_path_BD()+'\\06.ECE\\_data_\\ECE 2018\\BD4P.dta'     
        df = pd.read_stata(url,columns=['cod_mod7', 'anexo',"grupo_L","grupo_M"])
        
        df["cod_mod7"] =df['cod_mod7'].astype("str")
        df["anexo"] =df['anexo'].astype("int8")
        
        df.loc[(df['grupo_L'] == "< Nivel 1"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "Nivel 1"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "Nivel 2"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Nivel 3"), 'grupo_l3'] = 1
        
        df.loc[(df['grupo_M'] == "< Nivel 1"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "Nivel 1"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "Nivel 2"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Nivel 3"), 'grupo_m3'] = 1
        
        df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l0','grupo_l1',"grupo_l2",'grupo_l3',
                                                     'grupo_m0','grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

        df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l0']+df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
        df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_l0']+df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])


    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        return df

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "4P"
    df_group.fillna(0,inplace=True)
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]



def get_ECE_2S(anio=2019):
    if anio == 2019:
        url_ece = get_path_BD()+'\\06.ECE\\_data_\\ECE 2019\\Secundaria\\ECE_2019_2S_alumnos.xlsx'       
        df=pd.read_excel(url_ece, 'Base de datos', usecols="B,C,T,V",dtype={'cod_mod7':str,'anexo':'int8'})    
        
        df.loc[(df['grupo_L'] == "Previo al inicio"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "En inicio"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "En proceso"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Satisfactorio"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "Previo al inicio"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "En inicio"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "En proceso"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Satisfactorio"), 'grupo_m3'] = 1

        
    elif  anio == 2018:
        url =   get_path_BD()+'\\06.ECE\\_data_\\ECE 2018\\BD2S.dta'     
        df = pd.read_stata(url,columns=['cod_mod7', 'anexo',"grupo_L","grupo_M"])  
        df["cod_mod7"] =df['cod_mod7'].astype("str")
        df["anexo"] =df['anexo'].astype("int8")
        
        df.loc[(df['grupo_L'] == "< Nivel 1"), 'grupo_l0'] = 1
        df.loc[(df['grupo_L'] == "Nivel 1"), 'grupo_l1'] = 1
        df.loc[(df['grupo_L'] == "Nivel 2"), 'grupo_l2'] = 1
        df.loc[(df['grupo_L'] == "Nivel 3"), 'grupo_l3'] = 1

        df.loc[(df['grupo_M'] == "< Nivel 1"), 'grupo_m0'] = 1
        df.loc[(df['grupo_M'] == "Nivel 1"), 'grupo_m1'] = 1
        df.loc[(df['grupo_M'] == "Nivel 2"), 'grupo_m2'] = 1
        df.loc[(df['grupo_M'] == "Nivel 3"), 'grupo_m3'] = 1
        
    else:
        df = pd.DataFrame(columns = ["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"])
        return df


    df_group = df.groupby(['cod_mod7','anexo'])[['grupo_l0','grupo_l1',"grupo_l2",'grupo_l3',
                                                 'grupo_m0','grupo_m1',"grupo_m2",'grupo_m3']].agg("sum").reset_index()

    df_group['perc_satisf_l'] = df_group['grupo_l3']/(df_group['grupo_l0']+df_group['grupo_l1']+df_group['grupo_l2']+df_group['grupo_l3'])
    df_group['perc_satisf_m'] = df_group['grupo_m3']/(df_group['grupo_m0']+df_group['grupo_m1']+df_group['grupo_m2']+df_group['grupo_m3'])

    df_group.rename(columns={"cod_mod7": "COD_MOD","anexo": "ANEXO"},inplace=True)
    df_group["grado"] = "2S"
    
    
    return df_group[["COD_MOD","ANEXO","grado","perc_satisf_l","perc_satisf_m"]]


def get_ECE(anio=2019,cache=False):
    filename = 'ECE'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df
    
    df_2p=get_ECE_2P(anio)
    df_4p=get_ECE_4P(anio)
    df_2_4_p = pd.concat([df_2p,df_4p])
    
    df_2s=get_ECE_2S(anio)    
    df_p = df_2_4_p.groupby(['COD_MOD',"ANEXO"])[['perc_satisf_l',"perc_satisf_m"]].agg("max").reset_index()
    df_2s.drop('grado', axis=1, inplace=True)
    df = pd.concat([df_p,df_2s])
    df["ANEXO"] =df['ANEXO'].astype("int8")
    df["COD_MOD"] =df['COD_MOD'].astype("str") 
    hc.save_cache(df,filename,key_cache)
    
    return df


def get_Censo_Educativo(anio=2019,cache=False):

    filename = 'Evaluacion_Censal'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df

    if anio== 2020:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2020\\Local_lineal.dbf'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2020\\Local_pronoei_1.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P702']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P708']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P712']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P716']=="1") | 
                                                   (df_Local_Lineal['P716']=="2") | 
                                                   (df_Local_Lineal['P716']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P607']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P608']=="1") | 
                                                     (df_Local_Pronoei['P608']=="2") | 
                                                     (df_Local_Pronoei['P608']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
    
    elif anio== 2019:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2019\\Local_Lineal.DBF'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2019\\Local_Pronoei.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P702']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P708']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P711']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P716']=="1") | 
                                                   (df_Local_Lineal['P716']=="2") | 
                                                   (df_Local_Lineal['P716']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P605']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P608']=="1") | 
                                                     (df_Local_Pronoei['P608']=="2") | 
                                                     (df_Local_Pronoei['P608']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
        
    elif anio== 2018:
        url_Local_Lineal = get_path_BD()+'\\08.CensoEscolar\\_data_\\2018\\pLocal_2018.DBF'  
        dbf_Local_Lineal = Dbf5(url_Local_Lineal , codec='ISO-8859-1')
        df_Local_Lineal = dbf_Local_Lineal.to_dataframe()

        url_Local_Pronoei = get_path_BD()+'\\08.CensoEscolar\\_data_\\2018\\Localpronoei.dbf' 
        dbf_Local_Pronoei = Dbf5(url_Local_Pronoei , codec='ISO-8859-1')
        df_Local_Pronoei = dbf_Local_Pronoei.to_dataframe()    
        
        
        df_Local_Lineal['serv_int_1'] = np.where(df_Local_Lineal['P521']=="1",1,0)
        df_Local_Lineal['serv_luz_1'] = np.where(df_Local_Lineal['P506_1']=="1",1,0)
        df_Local_Lineal['serv_agua_1'] = np.where(df_Local_Lineal['P506_2']=="1",1,0)

        df_Local_Lineal['serv_desag_1'] = np.where((df_Local_Lineal['P506_3']=="1") | 
                                                   (df_Local_Lineal['P506_3']=="2") | 
                                                   (df_Local_Lineal['P506_3']=="2") ,1,0)
        


        df_Local_Pronoei['serv_luz_2'] = np.where(df_Local_Pronoei['P606']=="1",1,0)
        df_Local_Pronoei['serv_agua_2'] = np.where(df_Local_Pronoei['P607']=="1",1,0)

        df_Local_Pronoei['serv_desag_2'] = np.where((df_Local_Pronoei['P609']=="1") | 
                                                     (df_Local_Pronoei['P609']=="2") | 
                                                     (df_Local_Pronoei['P609']=="3") ,1,0)
        
        df_Local_Lineal=df_Local_Lineal[["CODLOCAL",'serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1']].copy()
        df_Local_Pronoei=df_Local_Pronoei[["COD_MOD","ANEXO",'serv_luz_2','serv_agua_2','serv_desag_2']].copy()
    else: 

        return pd.DataFrame(columns =["COD_MOD","ANEXO",'luz','agua','desague'])
        
    df_Local_Pronoei["ANEXO"] =df_Local_Pronoei['ANEXO'].astype("int8")

    dfser = get_df_servicios(anio=anio,columns=['COD_MOD', 'ANEXO', 'CODLOCAL'])
    dfser = pd.merge(dfser,df_Local_Lineal,left_on="CODLOCAL",right_on="CODLOCAL",how="left")
    dfser = pd.merge(dfser,df_Local_Pronoei,left_on=["COD_MOD","ANEXO"],right_on=["COD_MOD","ANEXO"],how="left")

    dfser.loc[(dfser['serv_luz_1'] == 1 )  | (dfser['serv_luz_2'] == 1 ), 'luz'] = 1
    dfser.loc[(dfser['serv_luz_1'] == 0 )  | (dfser['serv_luz_2'] == 0 ), 'luz'] = 0

    dfser.loc[(dfser['serv_agua_1'] == 1 )  | (dfser['serv_agua_2'] == 1 ), 'agua'] = 1
    dfser.loc[(dfser['serv_agua_1'] == 0 )  | (dfser['serv_agua_2'] == 0 ), 'agua'] = 0

    dfser.loc[(dfser['serv_desag_1'] == 1 )  | (dfser['serv_desag_2'] == 1 ), 'desague'] = 1
    dfser.loc[(dfser['serv_desag_1'] == 0 )  | (dfser['serv_desag_2'] == 0 ), 'desague'] = 0
    dfser.drop(columns=['CODLOCAL','serv_int_1','serv_luz_1','serv_agua_1','serv_desag_1','serv_luz_2','serv_agua_2','serv_desag_2'],inplace=True)
    
    dfser["ANEXO"] =dfser['ANEXO'].astype("int8")
    
    hc.save_cache(dfser,filename,key_cache)
    
    return dfser
    



def get_traslados_por_anio(anio,TIPO_TRASLADO='EN EL MISMO AÑO',modalidad="EBR"):
    path_file = get_path_BD_siagie_procesado()
    url_trasl = path_file+'\\Siagie_Traslados_{}.csv'.format(anio)
    sep = "|"
    encoding = 'latin-1'
    cols_tras = ['ID_PERSONA','TIPO_TRASLADO']

    #df_trasl = pd.read_csv(url_trasl ,encoding='utf-8',usecols=cols_tras,  sep=sep,dtype={'PERSONA_NRO_DOC':str})
    df_trasl = pd.read_csv(url_trasl ,encoding=encoding,usecols=cols_tras,  sep=sep,dtype={'ID_PERSONA':int})
    #if(anio==2019):
        #df_trasl = df_trasl[df_trasl.TIPO_TRASLADO==TIPO_TRASLADO].copy()
        #df_trasl.reset_index(drop=True,inplace=True)
 
    df_agg_t  = df_trasl.assign(
     TOTAL_TRASLADOS =   1
    ).groupby(['ID_PERSONA']).agg({'TOTAL_TRASLADOS':'sum'})

    df_agg_t.sort_values(by='TOTAL_TRASLADOS', ascending=False,inplace=True)
    df_agg_t.reset_index(inplace=True)
    
    return df_agg_t



def get_traslados_a_publico(anio,df_servicios=None,modalidad="EBR"):
    
    if df_servicios is None:
        df_servicios = get_df_servicios()
    
    path_file = get_path_BD_siagie_procesado()
    url_trasl = path_file+'/Siagie_Traslados_{}.csv'.format(anio)
    sep = "|"
    encoding = 'latin-1'
    cols_tras = ['ID_PERSONA','TIPO_TRASLADO','COD_MOD_ORIGEN','ANEXO_ORIGEN','COD_MOD_DESTINO','ANEXO_DESTINO']

    cl_s = ["COD_MOD","ANEXO","ES_PUBLICO"]
    #df_trasl = pd.read_csv(url_trasl ,encoding='utf-8',usecols=cols_tras,  sep=sep,dtype={'PERSONA_NRO_DOC':str})
    df_trasl = pd.read_csv(url_trasl ,encoding=encoding,usecols=cols_tras,  sep=sep,dtype={'ID_PERSONA':int,
                                                                                           'COD_MOD_ORIGEN':str,
                                                                                           'ANEXO_ORIGEN':int,
                                                                                           'COD_MOD_DESTINO':str,                                                                                           
                                                                                           'ANEXO_DESTINO':int,
                                                                                            })

    df_trasl_origen = pd.merge(df_trasl,df_servicios[cl_s],left_on=["COD_MOD_ORIGEN","ANEXO_ORIGEN"],
                               right_on=["COD_MOD","ANEXO"],how="inner")

    df_trasl_origen.drop(columns=['COD_MOD', 'ANEXO'],inplace=True)
    df_trasl_origen.rename(columns={'ES_PUBLICO': 'ES_PUBLICO_ORIGEN'}, inplace=True)


    df_trasl_destino = pd.merge(df_trasl_origen,df_servicios[cl_s],left_on=["COD_MOD_DESTINO","ANEXO_DESTINO"],
                               right_on=["COD_MOD","ANEXO"],how="inner")

    df_trasl_destino.drop(columns=['COD_MOD', 'ANEXO'],inplace=True)
    df_trasl_destino.rename(columns={'ES_PUBLICO': 'ES_PUBLICO_DESTINO'}, inplace=True)

    df_trasl_destino['TRASLADO_A_PUBLICO'] = np.where((df_trasl_destino.ES_PUBLICO_ORIGEN==0) & 
                                                      (df_trasl_destino.ES_PUBLICO_DESTINO==1),1,0)


    df_trasl_destino = df_trasl_destino[df_trasl_destino["TRASLADO_A_PUBLICO"]==1].copy()
    
    df_agg_t  = df_trasl_destino.assign(
     TOTAL_TRASLADOS =   1
    ).groupby(['ID_PERSONA']).agg({'TOTAL_TRASLADOS':'sum'})

    df_agg_t.sort_values(by='TOTAL_TRASLADOS', ascending=False,inplace=True)
    df_agg_t.reset_index(inplace=True)
    

    return df_agg_t



def get_df_notas(anio):
    
    path_file = get_path_BD_siagie_procesado()
    dtype = {'COD_MOD':str,'ANEXO':np.int8,'NOTA_AREA_REGULAR':np.int8,'DA':str}    
    url_notas = path_file+'\\NOTAS_POR_ALUMNO_{}.csv'.format(anio)
    df_notas = pd.read_csv(url_notas ,encoding='utf-8', dtype=dtype)
    
    return df_notas


def get_df_servicios(macro_region=None,region=None,anio=None,totales=False,geo=False,columns=[],full=False):
    print("Imprimiendo el anio servicio ",anio)
    
    anio_min = 2016
    if (anio is not None and anio<anio_min):        
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web.dbf"        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        print("No existe data de servicios menor que {}".format(anio_min)," se usara una bd referencial")
    
    elif anio is None:
        #print("Extrayendo servicios general")
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web.dbf"        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        
    elif anio<=2020:
        url =   get_path_BD()+"\\03.Servicios\\_data_\\Padron_web_{}.dbf".format(anio)        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        if anio==2016:
            df_codii_dre =  pd.read_csv(get_path_BD() + "\\03.Servicios\\_data_\\CODOOII_D_REGION.csv",dtype={'CODOOII': str})
            df_servicios = pd.merge(df_servicios,df_codii_dre,left_on="CODOOII",right_on="CODOOII",how="inner")
            df_servicios.rename(columns={'D_AREASIG': 'DAREACENSO'}, inplace=True)       
        
    elif anio>=2021:        
                
        url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web_2021.dbf"        
        dbf_ser = Dbf5(url , codec='ISO-8859-1')
        df_servicios = dbf_ser.to_dataframe()
        df_servicios.columns = map(lambda x: str(x).upper(), df_servicios.columns)
        #url =   get_path_BD() + "\\03.Servicios\\_data_\\Padron_web_2021.dta"        
        #df_servicios = pd.read_stata(url)   
        #df_servicios.columns = map(lambda x: str(x).upper(), df_servicios.columns)
        
    if full:
        df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        #return df_servicios    

    elif len(columns)>0:
        if "ANEXO" in df_servicios:
            df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        df_servicios =  df_servicios[columns].copy() 
    else:
        
        cls = ["COD_MOD","ANEXO","GESTION","DAREACENSO",'D_TIPSSEXO','D_REGION']
        if totales:
            cls = cls + ['TALUM_HOM','TALUM_MUJ','TALUMNO', 'TDOCENTE', 'TSECCION']        
            
        if geo:
            cls = cls + ['CODGEO','CODOOII','NLAT_IE', 'NLONG_IE']
        
        df_servicios = df_servicios[cls].copy() 
        df_servicios["ANEXO"] =df_servicios['ANEXO'].astype("int8")
        df_servicios["GESTION"] =df_servicios['GESTION'].astype("int8")    
    
        #df_servicios["AREA_CENSO"] =df_servicios['AREA_CENSO'].astype("int8")
        df_servicios['ES_PUBLICO'] = np.where(df_servicios['GESTION'].isin([1,2]),1,0)
        df_servicios['ES_URBANA'] = np.where(df_servicios['DAREACENSO']=='Urbana',1,0)
        df_servicios['ES_MIXTO'] = np.where(df_servicios['D_TIPSSEXO']=='Mixto',1,0)
        df_servicios['COD_MOD']=df_servicios['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
        
        df_servicios.drop(['GESTION', 'DAREACENSO', 'D_TIPSSEXO'], axis=1,inplace=True)
    
    if macro_region is not None:
        l_mr = get_macro_region(macro_region)
        df_servicios = df_servicios[df_servicios["D_REGION"].isin(l_mr)].copy()
    
    if region is not None:
        df_servicios = df_servicios[df_servicios["D_REGION"]==region].copy()
        
    return df_servicios


def get_desertores_por_anio(anio,modalidad="EBR"):
    
    path_file = get_path_BD_siagie_procesado()
    if(modalidad=="EBR"):
        url = path_file+"\\DESERCION\\DESERCION_{}"
    elif(modalidad=="EBE"):
        url = path_file+"\\DESERCION\\DESERCION_EBE_{}"
        
    anios_str=str(anio)+"_"+str(anio+1)
    ds = pd.read_csv(url.format("{}.csv".format(anios_str)))

    return ds


def get_shock_economico(anio,cache=False):
    
    filename = 'shock_economico'
    df = None
    key_cache = hc.get_key_cache([anio])
    print(key_cache)
    if cache:
        df = hc.get_cache(filename,key_cache)
        
    if df is not None:
        return df
    
    columns_n = ["ID_PERSONA","LOG_ING_T_MAS_1_IMP_DIST","NA_LOG_ING_T_MAS_1_IMP_DIST"] 
    dtypes_columns={'ID_PERSONA':int}
    
    if anio ==2022:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_EBE_2022_v2.csv.csv"
        ds_ = pd.read_csv(url,usecols=columns_n,dtype=dtypes_columns)
        
    elif anio ==2020:  
        
        url_ini = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_INI_2020_v2.csv"
        ds_ini =  pd.read_csv(url_ini,usecols=columns_n,dtype=dtypes_columns)
        
        url_ebr = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBR_2020_v2.csv"
        ds_ebr =  pd.read_csv(url_ebr,usecols=columns_n,dtype=dtypes_columns)    
        
        url_ebe = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_EBE_2020_v2.csv"
        ds_ebe =  pd.read_csv(url_ebe,usecols=columns_n,dtype=dtypes_columns)    
            
        ds_ = pd.concat([ds_ini, ds_ebr,ds_ebe])       

    else:
        url = get_path_BD()+"\\05.Schock_economico\\_data_\\procesado\\workfile_{}_{}_v2.csv".format("EBR",anio) 


    if anio ==2020:
        print("ds_ : ",ds_.shape)
        ds_["INGRESO_SIN_LOG"] = np.exp(ds_["LOG_ING_T_MAS_1_IMP_DIST"])
        
        df_siagie_ebr = get_siagie_por_anio(anio,modalidad="EBR",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  
        df_siagie_ebe = get_siagie_por_anio(anio,modalidad="EBE",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  
        
        df_siagie = pd.concat([df_siagie_ebr, df_siagie_ebe])  
        print("df_siagie : ",df_siagie.shape)
        df_serv = get_df_servicios(anio=anio,columns=["COD_MOD","ANEXO","CODGEO"])
        df_merge = pd.merge(df_siagie, df_serv, left_on=["COD_MOD","ANEXO"], right_on=["COD_MOD","ANEXO"],  how='inner')      
        print("df_merge : ",df_merge.shape)
        
        
        df_merge_schok = pd.merge(df_merge, ds_, left_on="ID_PERSONA", right_on="ID_PERSONA",  how='left')
        print("df_merge_schok : ",df_merge_schok.shape)
        
        df_merge_schok['INGRESO_SIN_LOG'] = df_merge_schok['INGRESO_SIN_LOG'].fillna(df_merge_schok.groupby(['ID_NIVEL','CODGEO'])['INGRESO_SIN_LOG'].transform('mean')) 
        df_merge_schok['INGRESO_CON_LOG'] = np.log(df_merge_schok['INGRESO_SIN_LOG'])            
        
        df_merge_schok.loc[(df_merge_schok['LOG_ING_T_MAS_1_IMP_DIST'].isna()), 'LOG_ING_T_MAS_1_IMP_DIST'] = df_merge_schok['INGRESO_CON_LOG']
        df_merge_schok.loc[(df_merge_schok['NA_LOG_ING_T_MAS_1_IMP_DIST'].isna()), 'NA_LOG_ING_T_MAS_1_IMP_DIST'] = 1
    
        df_merge_schok.drop(columns=['ID_NIVEL','COD_MOD','ANEXO','INGRESO_SIN_LOG', 'INGRESO_CON_LOG'],inplace=True)
        
        hc.save_cache(df_merge_schok,filename,key_cache)
        return df_merge_schok
    else:
        
        hc.save_cache(ds_,filename,key_cache)
        return ds_

def get_sisfoh():
    url_sisfoh = get_path_BD()+'\\04.SISFOH\\_data_\\NOMINAL_SISFOH.csv'
    cols = ['PERSONA_NRO_DOC','SISFOH_CSE']    
    df_sisfoh = pd.read_csv(url_sisfoh ,usecols=cols, encoding='utf-8', dtype={'PERSONA_NRO_DOC':str})
    df_sisfoh.drop_duplicates(subset ="PERSONA_NRO_DOC", keep = "last", inplace = True)
    return df_sisfoh


def get_distancia_prim_sec():
    
    url_ddist = get_path_BD() + "\\03.Servicios\\_data_\\SecundariaCerca.csv"
    df_sec_cerca =pd.read_csv(url_ddist, encoding="utf-8",index_col=0) 

    df_sec_cerca.loc[(df_sec_cerca['Distancia'] == 0), 'GRUPO_DISTANCIA'] = '0K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 0) & (df_sec_cerca['Distancia'] <= 1000), 'GRUPO_DISTANCIA'] = 'MENOR_1K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 1000) & (df_sec_cerca['Distancia'] <= 5000), 'GRUPO_DISTANCIA'] = '1K_5K'
    df_sec_cerca.loc[(df_sec_cerca['Distancia'] > 5000), 'GRUPO_DISTANCIA'] = 'MAYOR_5K'

    df_sec_cerca.columns = [x.upper() for x in df_sec_cerca.columns]

    df_sec_cerca[['COD_MOD','ANEXO']] = df_sec_cerca.CODIGOLUGAR.str.split("-",expand=True)
    df_sec_cerca['ANEXO'] = df_sec_cerca['ANEXO'].astype('uint8')

    df_sec_cerca['COD_MOD']=df_sec_cerca['COD_MOD'].apply(lambda x: '{0:0>7}'.format(x))
    del df_sec_cerca['SECUNDARIACERCA']
    del df_sec_cerca['CODIGOLUGAR']
    
    
    return df_sec_cerca







def get_siagie_por_anio(anio,id_grado=None,modalidad='EBR',modalidad_list=None,dtypes_columns=None,
                        columns_n= ['ID_PERSONA','ID_GRADO','ID_NIVEL','COD_MOD','ANEXO'],
                        id_persona_df=None,id_nivel=None,id_nivel_list=None,reduce_mem_usage=False):  
    
    
    columns_n_aux = []
    if 'ID_PERSONA' not in columns_n:
        columns_n_aux.append('ID_PERSONA')
        
    if 'ID_GRADO' not in columns_n:
        columns_n_aux.append('ID_GRADO')
        
    if 'ID_NIVEL' not in columns_n:
        columns_n_aux.append('ID_NIVEL')    
        
    columns_n_full = columns_n+columns_n_aux
    
    dtypes_columns_d = {'COD_MOD': str,
                  'ANEXO':int,
                  'ID_PERSONA':int,
                  'UBIGEO_NACIMIENTO_RENIEC':str,
                  'N_DOC':str,
                  'CODIGO_ESTUDIANTE':str,
                  'NUMERO_DOCUMENTO':str,
                  'N_DOC_APOD':str,
                  'CODOOII':str,
                  'ID_GRADO':'uint32',
                  'ESTADO_MAT':str,
                  'DSC_SECCION':str,
                  'ID_SECCION':str,
                  'SITUACION_MATRICULA':str,
                  'ID_NIVEL':str,
                  'SEXO':str,
                  'ANEXO': 'uint8'
                  
                  }
    
    if dtypes_columns is None:
        dtypes_columns = dtypes_columns_d

    id_niveles_inicial_ebr = ['A1','A2','A3','A5']
    if id_nivel  is not None:
        if id_nivel=="A0":      
            print("El nivel ficticio A0  sera reemplazado por los verdaderos niveles ",id_niveles_inicial_ebr)
            
    if id_nivel_list  is not None:
        if "A0" in id_nivel_list:    
            print("El nivel ficticio A0  sera reemplazado por los verdaderos niveles ",id_niveles_inicial_ebr)
     

    path_file = get_path_BD_siagie_procesado()
    
    if modalidad_list is None:
        modalidad_list = []
        modalidad_list.append(modalidad)
    
    multimodal = False
    if (len(modalidad_list)>1):
        multimodal = True
        
    list_df_total = []
    if ('EBR' in modalidad_list):    
        if(anio<2019):
            url = path_file+"\\NOMINAL_{}.csv"
            iter_pd = pd.read_csv(url.format(anio), usecols=columns_n_full,encoding="latin-1",sep="|",
                                  dtype=dtypes_columns,iterator=True, chunksize=500000)
            

            df = procesar_chunk_siagie(iter_pd,id_grado,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr)
        else:
            list_df = []
            for nivel in ["A0","B0","F0"]:               
                
                url = path_file+"\\NOMINAL_{}_{}.csv"
                iter_pd = pd.read_csv(url.format(nivel,anio), usecols=columns_n_full,encoding="latin-1",
                                      sep="|",dtype=dtypes_columns,iterator=True, chunksize=500000)
                
                df = procesar_chunk_siagie(iter_pd,id_grado,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr)
                list_df.append(df)
                
            df = pd.concat(list_df)
        if multimodal:    
            list_df_total.append(df)
            
    if('EBE' in modalidad_list):
            url = path_file+"\\NOMINAL_{}_{}.csv"
            df = pd.read_csv(url.format("EBE",anio), usecols=columns_n_full,encoding="latin-1",sep="|",dtype=dtypes_columns)
            if multimodal: 
                list_df_total.append(df)
                
    if multimodal:   
        df = pd.concat(list_df_total)
        
    df = df.drop_duplicates(subset=['ID_PERSONA'], keep='last')
    
    if reduce_mem_usage:
        return hd.reduce_mem_usage(df[columns_n])
    else:    
        return df[columns_n]


def procesar_chunk_siagie(iter_pd,id_grado,id_persona_df,id_nivel,id_nivel_list,id_niveles_inicial_ebr):
    chunk_list = []

    for chunk in iter_pd:
        if id_grado  is not None:
            chunk = chunk[(chunk['ID_GRADO'] == id_grado)] 
        if id_nivel  is not None:
            if id_nivel=="A0":     
                chunk = chunk[(chunk['ID_NIVEL'].isin(id_niveles_inicial_ebr))] 
            else:                  
                chunk = chunk[(chunk['ID_NIVEL'] == id_nivel)]  
        if id_nivel_list  is not None:
            if "A0" in id_nivel_list:    
                id_nivel_list.remove( "A0")                
                id_nivel_list = id_nivel_list + id_niveles_inicial_ebr                
            chunk = chunk[(chunk['ID_NIVEL'].isin(id_nivel_list))]  
        if id_persona_df is not None:
            #print(id_persona_df.shape)
            chunk = pd.merge(chunk, id_persona_df[['ID_PERSONA']], left_on="ID_PERSONA", right_on="ID_PERSONA", how='inner')
        chunk_list.append(chunk)
    return pd.concat(chunk_list)

