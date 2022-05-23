import pandas as pd
import requests as rs
import numpy as np
import datetime as datetime
from datetime import date
from dict2xml import dict2xml
import xmltodict

def FW_Auth (username,password,filetype):
    import requests as rs

    headers = {
    'accept': 'application/json',
    'content-type': 'application/x-www-form-urlencoded',}

    data = {
        'grant_type': 'password',
        'username': username,
        'password': password,
        }

    response = rs.post('https://api.freewheel.tv/auth/token', headers=headers, data=data).json()
    response['access_token']
    token = 'Bearer ' + response['access_token']
    
    
    headers = {'accept': 'application/'+str(filetype), 'authorization' : token, 'Content-Type': 'application/'+str(filetype),} 
    return(headers)

def create_placement(headers,io,name):
    import requests as rs
    from dict2xml import dict2xml
    import xmltodict
    headers = headers
    placement = {}
    placement['placement'] = {'insertion_order_id' : io}
    placement['placement']['name'] = name
    createpid = rs.post('https://api.freewheel.tv/services/v3/placement/create',headers=headers,data=dict2xml(placement))
    print(createpid.text)
    pid = xmltodict.parse(createpid.text,dict_constructor=dict)['placement']['id']
    print(pid)
    return pid


def update_schedule(start_date,end_date,headers,placement_id):
    import requests as rs
    from dict2xml import dict2xml
    import xmltodict
    from datetime import datetime
    fwe = str(datetime.strptime(end_date,'%m-%d-%Y'))
    end = fwe.split(' ')[0] + 'T23:59'
    fws = str(datetime.strptime(start_date,'%m-%d-%Y'))
    start = fws.split(' ')[0] + 'T00:00'
    placement = {}
    placement['placement'] = {'schedule': {'start_time': start , 'end_time' : end,'time_zone': '(GMT-05:00) America - New York'}}
    put_url = f'https://api.freewheel.tv/services/v3/placements/{placement_id}'
    data = dict2xml(placement)
    put_placement = rs.put(put_url,headers=headers,data=data).text
    print(put_placement)
    
    
def update_pricing(price_model,flat_fee_amount,headers,placement_id):
    import requests as rs
    from dict2xml import dict2xml
    import xmltodict
    
    if price_model == 'FLAT_FEE_SPONSORSHIP':
        placement = {}
        placement['placement'] = {'price': {'price_model': price_model, 'flat_fee_amount': flat_fee_amount}}
    
    else:
        placement = {}
        placement['placement'] = {'price' : {'price_model': price_model}}
    
    put_url = f'https://api.freewheel.tv/services/v3/placements/{placement_id}'
    data = dict2xml(placement)
    put_placement = rs.put(put_url,headers=headers,data=data).text
    return print(put_placement)




def update_audience_targeting(headers,list_of_ids,relation_in_set,relation_between_sets,exlcude,placement_id):
    
    import requests as rs
    
    import xmltodict   

    if len(list_of_ids) == 1:
        
        fw_set = {'set' : {'audience_item' : list_of_ids[0],'relation_in_set' : relation_in_set[0]}}
        
        dict_obj = {}
    
        dict_obj['audience_targeting'] = {'include' :fw_set }
    
        if type(exclude) == list:
        
            fw_set = {'set' : {'audience_item' : list_of_ids[0],'relation_in_set' : relation_in_set[0]}}
        
            dict_obj = {}
        
            dict_obj['audience_targeting'] = {'include' :fw_set }, {'exclude' : {'audience_item' : exclude }}
        

    if len(list_of_ids) == 2:
    
        set_list = []  
    
        for i in range(len(list_of_ids)):
        
            fw_set = {'audience_item' : list_of_ids[i],'relation_in_set' : relation_in_set[i]}
        
            set_list.append(fw_set)
        
        dict_obj = {}
    
        dict_obj['audience_targeting'] = {'include' : {'relation_between_sets': relation_between_sets[0] , 'set': set_list}}
    
        if type(exclude) == list:
        
            set_list = []  
    
            for i in range(len(list_of_ids)):
        
                fw_set = {'audience_item' : list_of_ids[i],'relation_in_set' : relation_in_set[i]}
        
                set_list.append(fw_set)
        
        dict_obj = {}
    
        dict_obj['audience_targeting'] = {'include' : {'relation_between_sets': relation_between_sets[0] , 'set': set_list}}, {'exclude' : {'audience_item' : exclude }}


    if len(list_of_ids) == 3:
    
        set_list = []  
    
        for i in range(len(list_of_ids)):
        
            fw_set = {'audience_item' : list_of_ids[i],'relation_in_set' : relation_in_set[i]}
        
            set_list.append(fw_set)
        
        dict_obj = {}
    
        dict_obj['audience_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}
    
        if type(exclude) == list:
        
            set_list = []  
    
            for i in range(len(list_of_ids)):
        
                fw_set = {'audience_item' : list_of_ids[i],'relation_in_set' : relation_in_set[i]}
        
                set_list.append(fw_set)
        
            dict_obj = {}
    
            dict_obj['audience_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}, {'exclude' : {'audience_item' : exclude }}
    
    data = dict2xml({'placement' : dict_obj})
    
    headers = headers
    
    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
    
    return put



def get_all_ids_and_names(headers,item,condition,per_page):
    import requests as rs
    headers = headers
    url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page=1&per_page={per_page}'
    get = rs.get(url,headers=headers).json()
    if item == 'audience_items':
        number_of_pages = get['audience_items']['total_page']
        last_page_number = len(get['audience_items']['items'])
        name_list = []
        id_list = []
        if type(condition) == str:
    
            for i in range(number_of_pages):
                url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={i+1}&per_page={per_page}'
                get = rs.get(url,headers=headers).json()
                for j in range(len(get['audience_items']['items'])):
                    name = get['audience_items']['items'][j]['name']
                    fwid = get['audience_items']['items'][j]['id']
                    if condition in name:
                        name_list.append(name)
                        print(name)
                        id_list.append(fwid)
                

            
            
        else:
    
            for i in range(number_of_pages):
                url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={i+1}&per_page={per_page}'
                get = rs.get(url,headers=headers).json()
                for j in range(len(get['audience_items']['items'])):
                    name = get['audience_items']['items'][j]['name']
                    print(len(name_list))
                    fwid = get['audience_items']['items'][j]['id']
                    name_list.append(name)
                    id_list.append(fwid)

    
    else:
        
        number_of_pages = get['total_page']
        last_page_number = len(get['items'])
        name_list = []
        id_list = []
        if type(condition) == str:
    
            for i in range(number_of_pages):
                url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={i+1}&per_page={per_page}'
                get = rs.get(url,headers=headers).json()
                for j in range(len(get['items'])):
                    name = get['items'][j]['name']
                    fwid = get['items'][j]['id']
                    if condition in name:
                        name_list.append(name)
                        print(name)
                        id_list.append(fwid)
                

            
            
        else:
    
            for i in range(number_of_pages):
                url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={i+1}&per_page={per_page}'
                get = rs.get(url,headers=headers).json()
                for j in range((len(get['items']))):
                    name = get['items'][j]['name']
                    fwid = get['items'][j]['id']
                    name_list.append(name)
                    print(name)
                    id_list.append(fwid)

                            
    
    
    
    tuple_list = []
    for i in range(len(name_list)):
        tup = (name_list[i],id_list[i])
        tuple_list.append(tup)
    
    return tuple_list




def get_last_page_for_FWitems(headers,item,per_page):

    url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page=1&per_page={per_page}'

    if item == 'audience_items':
        get = rs.get(url,headers=headers).json()
    
        last_page = get['audience_items']['total_page']

        url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={last_page}&per_page={per_page}'
    
        get = rs.get(url,headers=headers).json()

        num = len(get['audience_items']['items'])

        name_list = []
    
        id_list = []
        
        for i in range(num):
    
            name = get['audience_items']['items'][i]['name']

            fwid = get['audience_items']['items'][i]['id']

            name_list.append(name)
    
            id_list.append(fwid)


        
    else:
    
        get = rs.get(url,headers=headers).json()
    
        last_page = get['total_page']

        url = f'https://api.freewheel.tv/services/v4/{item}?status=ACTIVE&page={last_page}&per_page={per_page}'
    
        get = rs.get(url,headers=headers).json()

        num = len(get['items'])

        name_list = []
    
        id_list = []
        
        for i in range(num):
    
            name = get['items'][i]['name']

            fwid = get['items'][i]['id']

            name_list.append(name)
    
            id_list.append(fwid)
    
    
    tuple_list = []
    for i in range(len(name_list)):
        tup = (name_list[i],id_list[i])
    
        tuple_list.append(tup)
    
    return(tuple_list)

                            
    
    
    
    tuple_list = []
    for i in range(len(name_list)):
        tup = (name_list[i],id_list[i])
        tuple_list.append(tup)
    
    return tuple_list

def get_all_ioids_in_a_campaign(headers,campaign_id):
    
    headers=headers
    
    url = f"https://api.freewheel.tv/services/v3/campaign/{campaign_id}/insertion_orders?page=null&per_page=50&id=null&workflow_step_type=optional"

    get = rs.get(url,headers=headers).text

    parsedget = xmltodict.parse(get,dict_constructor=dict)

    numio = parsedget['insertion_orders']['@total_entries']

    name_list = []
    
    id_list = []

    for i in range(int(numio)):
        
        name = parsedget['insertion_orders']['insertion_order'][i]['name']
    
        io_id = parsedget['insertion_orders']['insertion_order'][i]['id']
    
        name_list.append(name)
    
        id_list.append(io_id)
    
    tuple_list = []
    
    for i in range(int(numio)):
    
        tup = (name_list[i],id_list[i])
    
        tuple_list.append(tup)
        
    return tuple_list




def get_placement_ids_from_io(headers,io_id):
    
    headers=headers

    url = f"https://api.freewheel.tv/services/v3/insertion_order/{io_id}/placements?insertion_order_id={io_id}&page=null&per_page=50"

    get = rs.get(url,headers=headers).text
    

    parsedget = xmltodict.parse(get,dict_constructor=dict)
    

    numio = parsedget['placements']['@total_entries']

    name_list = []
    
    id_list = []

    for i in range(int(numio)):
        
        name = parsedget['placements']['placement'][i]['name']
    
        io_id = parsedget['placements']['placement'][i]['id']
    
        name_list.append(name)
    
        id_list.append(io_id)
    
    tuple_list = []
    
    for i in range(int(numio)):
    
        tup = (name_list[i],id_list[i])
    
        tuple_list.append(tup)
        
    return tuple_list


def get_placement(header,fwid,node):
        import requests as rs
        headers = header
        from dict2xml import dict2xml
        from dict2xml import dict2xml
        import xmltodict
    
        get_url = f'https://api.freewheel.tv/services/v3/placements/{str(fwid)}?show={node}'
        get_placement = rs.get(get_url,headers=headers).text
        return xmltodict.parse(get_placement,dict_constructor=dict)



def update_content_targeting(headers,list_of_sets,relation_in_set,relation_between_sets,exclude,placement_id):
    
    import requests as rs
    
    from dict2xml import dict2xml
    
    import xmltodict 
    
    dict_obj = {}
    
    if len(list_of_sets) == 1:
        
        list_of_sets[0]['relation_in_set'] = relation_in_set[0]
        
        fw_set = list_of_sets[0]
    
        dict_obj['content_targeting'] = {'include' :{'set' :fw_set }}
    
        if type(exclude[0]) == dict:

            list_of_sets[0]['relation_in_set'] = relation_in_set[0]
        
            fw_set = list_of_sets[0]
        
            dict_obj = {}
    
            dict_obj['content_targeting'] = {'include' :{'set' :fw_set }} , {'exclude' :  exclude }
        
    if len(list_of_sets) == 2:
            
        set_list = []
        
        for i in range(len(list_of_sets)):
            
            list_of_sets[i]['relation_in_set'] = relation_in_set[i]
        
            fw_set = list_of_sets[i]
            
            set_list.append(fw_set)
            
            if type(exclude[0]) == dict:
            
                dict_obj['content_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}, {'exclude' :  exclude }
            
            else:
                
                dict_obj['content_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}
                
    if len(list_of_sets) == 3:
            
        set_list = []
        
        for i in range(len(list_of_sets)):
            
            list_of_sets[i]['relation_in_set'] = relation_in_set[i]
        
            fw_set = list_of_sets[i]
            
            set_list.append(fw_set)
            
            if type(exclude[0]) == dict:
            
                dict_obj['content_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}, {'exclude' :  exclude }
            
            else:
                
                dict_obj['content_targeting'] = {'include' : {'relation_between_sets': relation_between_sets , 'set': set_list}}
                
                   
    data = dict2xml({'placement' : dict_obj})
    
    headers = headers
    
    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
                  
    return put        



import xmltodict
    
from dict2xml import dict2xml
import requests as rs
def attach_ad_units(headers,placement_id,ad_units,prices):

    from dict2xml import dict2xml
    
    headers = headers
    
    au_list = []

    for i in range(len(ad_units)):
        
        au = {'ad_unit_id' : ad_units[i] , 'status' : 'ACTIVE', 'price': prices[i]}

        au_list.append(au)
        
    data = dict2xml({'placement' : {'ad_product':{'link_method': 'NOT_LINKED', 'ad_unit_node': au_list }}})
            
    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
                  
    return put




def attach_creatives(headers,placement_id,creatives):
    from dict2xml import dict2xml
    
    headers = headers
    
    get = rs.get(f'https://api.freewheel.tv/services/v3/placements/{placement_id}?show=all',headers=headers).text
    
    node = xmltodict.parse(get,dict_constructor=dict)
    
    number_of_nodes = len(node['placement']['ad_product']['ad_unit_node'])

    if number_of_nodes == 2:

        for i in range(number_of_nodes):
            aun = node['placement']['ad_product']['ad_unit_node'][i]['ad_unit_node_id']
            for j in range(len(creatives)):
                rs.put(f'https://api.freewheel.tv/services/v3/ad_unit_nodes/{aun}/creatives/{creatives[j]}.xml',headers=headers).text
                print(rs.put(f'https://api.freewheel.tv/services/v3/ad_unit_nodes/{aun}/creatives/{creatives[j]}.xml',headers=headers).text)

    else:

         aun = node['placement']['ad_product']['ad_unit_node']['ad_unit_node_id']
         for j in range(len(creatives)):
                rs.put(f'https://api.freewheel.tv/services/v3/ad_unit_nodes/{aun}/creatives/{creatives[j]}.xml',headers=headers).text
                print(rs.put(f'https://api.freewheel.tv/services/v3/ad_unit_nodes/{aun}/creatives/{creatives[j]}.xml',headers=headers).text)









def update_platform_targeting(headers,list_of_devices,placement_id):
    
    headers = headers
    
    dict_obj = {}
    
    dict_obj['device'] = list_of_devices
    
    data = dict2xml({'placement' :{'platform_targeting': dict_obj}})

    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
    
    return put




def update_geo_targeting(headers,inc_exc,geo_type,list_of_codes,placement_id):
    
        
    dict_obj = {}
        
    dict_obj['geography_targeting'] = {inc_exc :{geo_type: list_of_codes }}
        
    data = dict2xml({'placement' : dict_obj})

    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
    
    return put





def update_daypart_targeting(headers,list_of_days,start_time,end_time,timezone,placement_id):
    
    headers = headers
    
    day_list = []

    for i in range (len(list_of_days)):
    
        day = list_of_days[i].upper()
    
        part_dict = {'start_time' : start_time, 'end_time': end_time ,'start_day': day, 'end_day':day}
    
        day_list.append(part_dict)
    
    dict_obj['daypart_targeting']['part'] = day_list

    data = dict2xml({'placement' : dict_obj})

    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
    
    return put




def update_fcap(headers,number_of_fcaps,imps,time,placement_id):
    
    headers=headers
    
    fcap_list = []
    
    for i in range(number_of_fcaps):
    
        freq = {'value' : imps[i], 'type' : 'IMPRESSION', 'period' : time[i]}
    
        fcap_list.append(freq)
    
    dict_obj = {}

    dict_obj['delivery'] = {'priority': 'GUARANTEED',
     'pacing': 'SMOOTH_AS',
     'override_repeat_mode': 'NONE',
     'frequency_cap': fcap_list,
     'ignore_brand_frequency_cap': 'false',
     'excess_inventory': 'NETWORK_DEFAULT',
     'dynamic_ad_insertion': 'DYNAMIC_ENABLED',
     'excess_inventory_precondition': '0',
     'level_to_optimize_for_profit': 'NONE'}

    data = dict2xml({'placement' : dict_obj})

    put = rs.put(f'https://api.freewheel.tv/services/v3/placements/{placement_id}',headers=headers,data=data).text
   
    return put



def get_nightly_forecast(headers,placement_id):
    
    headers = headers
    
    url = f"https://api.freewheel.tv/services/v4/placements/{placement_id}/forecasts?type=nightly"

    get = rs.get(url,headers=headers).json()
    
    return(get)


def get_placement(header,fwid,node):
    import requests as rs
    headers = header
    from dict2xml import dict2xml
    from dict2xml import dict2xml
    import xmltodict
    
    get_url = f'https://api.freewheel.tv/services/v3/placements/{str(fwid)}?show={node}'
    get_placement = rs.get(get_url,headers=headers).text
    return xmltodict.parse(get_placement,dict_constructor=dict)
        
def run_forecast(headers,placement_id):
    
    headers=headers
    
    get_params = rs.post(f'https://api.freewheel.tv/services/v4/placements/{placement_id}/forecasts',headers=headers).json()
    return get_params 