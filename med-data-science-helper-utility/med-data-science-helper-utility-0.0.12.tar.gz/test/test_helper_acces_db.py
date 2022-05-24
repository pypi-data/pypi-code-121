
import pandas as pd
import numpy as np
import med_data_science_helper.helper_acces_db as hadb


print(hadb.get_path_BD())



df = hadb.get_nexus(anio=2015,cache=True,subtipo_trabajador=None)

df = hadb.get_ECE_2P()
df = hadb.get_ECE_4P()
df = hadb.get_ECE_2S()
df = hadb.get_ECE()

df = hadb.get_Censo_Educativo(anio=2019)

df = hadb.get_traslados_por_anio(2019)
df = hadb.get_traslados_a_publico(2019)

df = hadb.get_df_notas(2019)




df_se = hadb.get_shock_economico(2020,cache=False)

df_siagie_ebr = hadb.get_siagie_por_anio(2020,modalidad="EBR",columns_n= ['ID_PERSONA'])  

df_siagie_ebr_ = hadb.get_siagie_por_anio(2020,modalidad_list=["EBR"],columns_n= ['ID_PERSONA'])  

df_siagie_ebe = hadb.get_siagie_por_anio(2020,modalidad="EBE",columns_n= ['ID_PERSONA'])  
df_siagie_ebe_ = hadb.get_siagie_por_anio(2020,modalidad_list=["EBE"],columns_n= ['ID_PERSONA'])  

df_siagie_total = hadb.get_siagie_por_anio(2020,modalidad_list=["EBR","EBE"],columns_n= ['ID_PERSONA'])  



df_siagie_ebr = hadb.get_siagie_por_anio(2020,modalidad="EBR",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  




df_siagie_ebe = hadb.get_siagie_por_anio(2020,modalidad="EBE",columns_n= ['ID_PERSONA','ID_NIVEL','COD_MOD','ANEXO'])  

df_siagie = pd.concat([df_siagie_ebr, df_siagie_ebe])  
print(df_siagie.shape)

df_serv = hadb.get_df_servicios(anio=2020,columns=["COD_MOD","ANEXO","CODGEO"])
df_merge = pd.merge(df_siagie, df_serv, left_on=["COD_MOD","ANEXO"], right_on=["COD_MOD","ANEXO"],  how='inner') 
print(df_merge.shape)

8106218-8106187

df = hadb.get_sisfoh()

df = hadb.get_distancia_prim_sec()

df = hadb.get_siagie_por_anio(2020,id_nivel="A0")
