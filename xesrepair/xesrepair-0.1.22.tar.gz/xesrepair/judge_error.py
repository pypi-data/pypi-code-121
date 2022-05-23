# 库安装出错因为依赖被占用时，需要先卸载的库列表
UNINSTALL_LIST_MAP = {
    'numpy': ['numpy'],
    'pandas': ['numpy'],
    'pgzero': ['numpy'],
    'scipy': ['numpy'],
    'scikit-learn': ['numpy', 'scipy'],
    'seaborn': ['numpy', 'scipy', 'matplotlib', 'pandas'],
    'openpyxl': ['numpy'],
    'xes-lib': ['numpy'],
    'imageio':['numpy']
}

ERR_TYPE_MSG_MAP = {
    "PermissionError": ['PermissionError', 'FileExistsError: [WinError 183] 当文件已存在时，无法创建该文件'],
    'NoSpace': ['[Errno 28] No space left on device']
}


def fn_judge_error(msg, module_name):
    '''
    根据stderr的字符串返回是否
    @param msg stderr的字符串
    @return 返回一个成功对象 { "status": "ok" }或失败对象 { "status": "err", 'msg':'PermissionError', "uninstall_list": ['numpy']}
    注意：这里的uninstall_list中的库需要先卸载，再安装目标库
    '''

    check_result = {
        "status": "ok",

    }

    for err_type in ERR_TYPE_MSG_MAP:
        for err_msg in ERR_TYPE_MSG_MAP[err_type]:
            if err_msg in msg:
                print("触发了失败报错", err_type, err_msg)
                check_result["status"] = "err"
                check_result["msg"] = err_msg
                if module_name in UNINSTALL_LIST_MAP:
                    check_result['uninstall_list'] = UNINSTALL_LIST_MAP[module_name]
                else:
                    check_result['uninstall_list'] = []
                return check_result

    return check_result
