# -*- coding: utf-8 -*-
"""
Created on Fri May 27 11:48:20 2022

@author: User
"""

def get_niveles_grados_por_modalidad(modalidad,id_nivel_list=None, grado_list=None,rt_ngm=True,rt_key=False,rt_niveles=False):
    # returna lista de id grado, dsc grado y media de edad en ese grado por cada nivel educativo
    id_nivel_list_ = [] 
    if modalidad=="EBE":
        id_nivel_list_ = ["E0","E1","E2"]
    elif modalidad=="EBR":
        id_nivel_list_ = ["A1","A2","A3","A5","B0","F0"]
    else:
        return
    
    if id_nivel_list is None:
        id_nivel_list = id_nivel_list_
    
    list_dict_niv_gr = []   
     
    
    for id_nivel_ in id_nivel_list:
        dict_niv_gr={}
        list_id_grados_ = []
        list_dsc_grados_ = []
        if id_nivel_=="E0":
            list_id_grados_ = [(1,"0 a 2 anios",1)]
            
            
        if id_nivel_=="E1":
            list_id_grados_ = [(3,"3 anios",3),(4,"4 anios",4),(5,"5 anios",5)]
            
        if id_nivel_=="E2":
            list_id_grados_ = [(6,"Primaria PRIMERO",7),(7,"Primaria SEGUNDO",8),(8,"Primaria TERCERO",10),(9,"Primaria CUARTO",11),(10,"Primaria QUINTO",13),(11,"Primaria SEXTO",14)]
        
        if id_nivel_=="A1":
            list_id_grados_ = [(1,"0 a 2 anios",2)]
        
        if id_nivel_=="A2":
            list_id_grados_ = [(3,"Grupo 3 anios",3),(4,"Grupo 4 anios",4),(5,"Grupo 5 anios",5)]
            
        if id_nivel_=="A3":
            list_id_grados_ = [(1,"0 a 2 anios",2),(2,"3 anios",3),(3,"4 anios",4),(4,"5 anios",5)]
            
        if id_nivel_=="A5":
            list_id_grados_ = [(1,"0 a 2 anios",2),(2,"3 anios",3),(3,"4 anios",4),(4,"5 anios",5)]
        
        if id_nivel_=="B0":
            list_id_grados_ = [(4,"PRIMERO",6),(5,"SEGUNDO",7),(6,"TERCERO",8),(7,"CUARTO",9),(8,"QUINTO",10),(9,"SEXTO",11)]
            
        if id_nivel_=="F0":
            list_id_grados_ = [(10,"PRIMERO",12),(11,"SEGUNDO",13),(12,"TERCERO",14),(13,"CUARTO",15),(14,"QUINTO",16)]  
            
        dict_niv_gr["id_nivel"]=id_nivel_
        
        if grado_list is not None:
            dict_niv_gr["list_grados"]=grado_list
        else:
            dict_niv_gr["list_grados"]=list_id_grados_
            
        list_dict_niv_gr.append(dict_niv_gr)
    
    list_return = []
    if (rt_ngm):    
        list_return.append(list_dict_niv_gr)
        
    list_niveles = []   
        
    list_key = []
    list_key.append(modalidad)
    
    for item in list_dict_niv_gr:

        id_nivel = item["id_nivel"]
        list_niveles.append(id_nivel)
        list_grados = item["list_grados"]
        list_key.append(str(id_nivel))

        for grado in list_grados:

            if isinstance(grado, tuple):
                ID_GRADO = grado[0]
            else:
                ID_GRADO = grado

            list_key.append(str(ID_GRADO))

    key_str = '_'.join(list_key)
    
    if rt_key:
        list_return.append(key_str)
        
    if rt_niveles:
        list_return.append(list_niveles)
        
    return tuple(list_return) if len(list_return)>1 else list_return[0]