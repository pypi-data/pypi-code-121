"""
converter allow converting db data to nice format. data of db structured the next way. {1:{data},2{data}}
but when we send data over internet indexes are ruin the sorting of data.
we need to achieve the next format  -> [{obj1},{obj2},{obj3}]
also the obj should have own id which represent dbs index -> {data..., id:index}
"""


def convert_to_api_format(db_hash):
    api_data_format = []
    for index, obj in db_hash.items():
        api_obj = {'id': index}
        api_obj.update(obj)
        api_data_format.append(api_obj)
    return api_data_format
