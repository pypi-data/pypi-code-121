def select_columns(data, cfg=None):
    return_meta = []
    return_result = []

    column_list = cfg['columns_name'].strip().split(',')

    # form code_list
    code_list = []
    for tmp_dict in data['meta']:
        code_list.append(tmp_dict['code'])
    # the index list of selected column in data
    selected_column_index_list = []
    for code in column_list:
        selected_column_index_list.append(code_list.index(code))
        return_meta.append(data['meta'][code_list.index(code)])
    for i in range(len(data['result'])):
        tmp_list = []
        for j in selected_column_index_list:
            tmp_list.append(data['result'][i][j])
        return_result.append(tmp_list)

    data['meta'] = return_meta
    data['result'] = return_result

    return data