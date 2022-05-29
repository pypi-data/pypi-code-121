import re

def generate_dict_path(key_name, item, path_list):
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, dict) or isinstance(value,list):
                generate_dict_path(key_name + "/" + key, value, path_list)
            else:
                path_list.append(key_name + "/" + key)
    elif isinstance(item,list):
        for v in range(len(item)):
            if isinstance(item[v], dict) or isinstance(item[v],list):
                generate_dict_path(key_name + "/" + "setoptlist(" + str(v) + ")", item[v], path_list)
            else:
                path_list.append(key_name + "/" + "setoptlist(" + str(v) + ")")
    else:
        pass


def check_list_key_illegal(keyname):
    if len(re.findall(r"setoptlist\(\d+\)", keyname)) != 0:
        return True
    else:
        return False


def get_list_key_index(keyname):
    keyname = keyname.replace("setoptlist(","")
    keyname = keyname.replace(")","")
    return keyname


def get_value_by_key(dict_data, keyname):
    result_list = list()
    routine_list = get_path_by_key(dict_data, keyname)
    for routine in routine_list:
        path_list = routine.split("/")[1:]
        dst_val = dict_data.copy()
        for path in path_list:
            if check_list_key_illegal(path):
                num = path.replace("setoptlist(", "")
                num = num.replace(")", "")
                dst_val = dst_val[int(num)]
            else:
                dst_val = dst_val[path]
            if path == keyname:
                result_list.append(dst_val)
    return result_list


def get_key_by_value(dict_data,value,convert=False):
    result_list = list()
    routine_list = list()
    generate_dict_path("", dict_data, routine_list)
    for routine in routine_list:
        cache_routine = []
        path_list = routine.split('/')[1:]
        dst_val = dict_data.copy()
        for path in path_list:
            cache_routine.append(path)
            if check_list_key_illegal(path):
                num = path.replace("setoptlist(", "")
                num = num.replace(")", "")
                dst_val = dst_val[int(num)]
            else:
                dst_val = dst_val[path]
            if dst_val == value:
                cache_routine_str = "/" + "/".join(cache_routine)
                if convert == True:
                    cache_routine_str = convert_dict_path(cache_routine_str)
                result_list.append(cache_routine_str)
    return list(set(result_list))


def get_all_by_key(dict_data, keyname,convert=False):
    result_list = list()
    routine_list = get_path_by_key(dict_data, keyname)
    cache_last = []
    for routine in routine_list:
        path_list = routine.split("/")[1:]
        dst_val = dict_data.copy()
        cache_routine = ['']
        for path in path_list:
            cache_routine.append(path)
            if check_list_key_illegal(path):
                num = path.replace("setoptlist(", "")
                num = num.replace(")", "")
                dst_val = dst_val[int(num)]
            else:
                dst_val = dst_val[path]
            if path == keyname:
                cache_routine_str = "/".join(cache_routine)
                if convert == True:
                    cache_routine_str = convert_dict_path(cache_routine_str)
                if cache_routine_str not in cache_last:
                    cache_last.append(cache_routine_str)
                    single_result = {"path":cache_routine_str,"value":dst_val}
                    result_list.append(single_result)
    return result_list


def get_path_by_key(dict_data, keyname,convert=False):
    all_path = list()
    routine_list = list()
    generate_dict_path("", dict_data, routine_list)
    for routine in routine_list:
        path_list = routine.split('/')[1:]
        if keyname in path_list:
            if check_list_key_illegal(path_list[-1]):
                routine = "/".join(routine.split("/")[0:-1])
            if convert == True:
                routine = convert_dict_path(routine)
            all_path.append(routine)
    return list(set(all_path))


def get_path_by_value(dict_data, value,convert=False):
    result_list = list()
    routine_list = list()
    generate_dict_path("", dict_data, routine_list)
    for routine in routine_list:
        path_list = routine.split('/')[1:]
        dst_val = dict_data.copy()
        for path in path_list:
            if check_list_key_illegal(path):
                num = path.replace("setoptlist(", "")
                num = num.replace(")", "")
                dst_val = dst_val[int(num)]
            else:
                dst_val = dst_val[path]
            if dst_val == value:
                if "setoptlist(" in  routine.split("/")[-1]:
                    routine = "/".join(routine.split("/")[0:-2])
                else:
                    routine = "/".join(routine.split("/")[0:-1])
                if routine == "":
                    routine = "/"
                if convert == False:
                    result_list.append(routine)
                else:
                    routine = convert_dict_path(routine)
                    result_list.append(routine)

    return list(set(result_list))


def search_all_by_str(dict_data,search_str,convert=False):
    key_result = get_value_by_key(dict_data,search_str)
    value_result = get_key_by_value(dict_data,search_str)
    value_in_result = search_key_in_value(dict_data,search_str)
    combine_list = [element for i in [key_result,value_result,value_in_result] for element in i]
    if convert == True:
        return list(set([convert_dict_path(element) for element in combine_list]))
    else:
        return list(set(combine_list))


def search_key_in_value(dict_data, value,convert=False):
    result_list = list()
    routine_list = list()
    generate_dict_path("", dict_data, routine_list)
    for routine in routine_list:
        cache_routine = [""]
        path_list = routine.split('/')[1:]
        dst_val = dict_data.copy()
        for path in path_list:
            cache_routine.append(path)
            if check_list_key_illegal(path):
                num = path.replace("setoptlist(", "")
                num = num.replace(")", "")
                dst_val = dst_val[int(num)]
            else:
                dst_val = dst_val[path]
            if isinstance(value,str):
                if value in dst_val:
                    result_list.append("/".join(cache_routine))
                    break
            elif isinstance(dst_val,list) and isinstance(value,list):
                if value == dst_val:
                    result_list.append("/".join(cache_routine))
                    break
            else:
                pass
    if convert == True:
        result_list = [convert_dict_path(i) for i in result_list]
    return list(set(result_list))


def convert_dict_path(path):
    dict_path = "dict"
    path_list = path.split("/")[1:]
    for path in path_list:
        if check_list_key_illegal(path):
            index = get_list_key_index(path)
            dict_path = dict_path + "[%s]" % index
        else:
            dict_path = dict_path + "[\'%s\']" % path
    return dict_path


def get_value_by_path(dict_data,path_str):
    path_list = path_str.split("/")[1:]
    dst_val = dict_data.copy()
    for path in path_list:
        if check_list_key_illegal(path):
            num = path.replace("setoptlist(", "")
            num = num.replace(")", "")
            dst_val = dst_val[int(num)]
        else:
            dst_val = dst_val[path]
    return dst_val

