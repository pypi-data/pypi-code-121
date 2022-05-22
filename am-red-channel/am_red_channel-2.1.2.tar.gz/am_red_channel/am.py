
import requests as _req
from am_red_channel._consts import *

def AM_SendDataSameDevice(id, data):
    id_url = k_AM_localNodeURL + str(id)    
    
    hConfigurations = {
        'Content-Type': k_AM_contentType,
    }
    
    params = {          
        'AM_Auth_Token': 'Amr Mostafa (Amr_MAM)', 
        'AM_Auth_Signature': 'AM-from-Python',
    }

    try:
        response  = _req.request(k_AM_SEND, id_url, headers=hConfigurations, params=params, data = str(data))
        if(response.status_code == 200) :
            return K_AM_success
        else :
            return k_AM_failure
    except:
        return k_AM_failed_to_connect


def AM_GetDataSameDevice(id):
    id_url = k_AM_localNodeURL + str(id)   

    hConfigurations={
        'Content-Type': k_AM_contentType,
    }

    params = {          
        'AM_Auth_Token': 'Amr Mostafa (Amr_MAM)', 
        'AM_Auth_Signature': 'AM-from-Python',
    }

    try:
        response  = _req.request(k_AM_GET, id_url, headers=hConfigurations, params=params)
        return response.text
    except:
        return k_AM_failed_to_connect



def AM_SendData(id, node_red_url, data):
    id_url = ""
    
    if(str(node_red_url).endswith('/')):
        id_url = str(node_red_url) + str(id)
    else :
        id_url = str(node_red_url) + "/" + str(id)

    hConfigurations={
        'Content-Type': k_AM_contentType,
    }
    
    params = {          
        'AM_Auth_Token': 'Amr Mostafa (Amr_MAM)', 
        'AM_Auth_Signature': 'AM-from-Python',
    }

    try:
        response  = _req.request(k_AM_SEND, id_url, headers=hConfigurations, params=params, data = str(data))
        if(response.status_code == 200) :
            return K_AM_success
        else :
            return k_AM_failure
    except:
        return k_AM_failed_to_connect



def AM_GetData(id, node_red_url):
    id_url = ""
    
    if(str(node_red_url).endswith('/')):
        id_url = str(node_red_url) + str(id)
    else :
        id_url = str(node_red_url) + "/" + str(id)

    hConfigurations={
        'Content-Type': k_AM_contentType,
    }

    params = {          
        'AM_Auth_Token': 'Amr Mostafa (Amr_MAM)', 
        'AM_Auth_Signature': 'AM-from-Python',
    }

    try:
        response  = _req.request(k_AM_GET, id_url, headers=hConfigurations, params=params)
        return response.text
    except:
        return k_AM_failed_to_connect

