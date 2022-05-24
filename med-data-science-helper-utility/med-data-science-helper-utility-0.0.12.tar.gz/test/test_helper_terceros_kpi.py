# -*- coding: utf-8 -*-

import med_data_science_helper.helper_terceros_kpi as htk
import med_data_science_helper.helper_acces_db as hadb


df_siagie = hadb.get_siagie_por_anio(2021,id_nivel="F0",columns_n= ['ID_PERSONA',"COD_MOD"])
df_siagie2 = htk.agregar_nexus(df_siagie,anio_df=2021,anio_h=2020, cache=False )
df_siagie3 = htk.agregar_pivot_juntos(df_siagie,anio_df=2021,anio_h=2021,t_anios=3,delete_juntos_t_vcc=True, cache=False )

print(df_siagie3.columns)


print(df_siagie3.JUNTOS_T.value_counts())
print(df_siagie3.JUNTOS_T.isna().value_counts())

print(df_siagie3.JUNTOS_T_MENOS_1.isna().value_counts())
print(df_siagie3.JUNTOS_T_MENOS_1.value_counts())

print(df_siagie3.JUNTOS_T_MENOS_2.value_counts())
print(df_siagie3.JUNTOS_T_MENOS_2.isna().value_counts())
