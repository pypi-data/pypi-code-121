import os
import pickle
import time

DATA_FOLD = 'openfc_data'


def db_save(db_file_name: str, data):
    data_fold = db_get_data_fold()
    db_file = data_fold + db_file_name + '.dat'
    with open(db_file, 'wb') as f:
        # Pickle the 'data' dictionary using the highest protocol available.
        update_time = time.time()
        pickle.dump(update_time, f)
        pickle.dump(data, f)


def db_load(db_file_name: str):
    data_fold = db_get_data_fold()
    last_update_time = 0
    db_file = data_fold + db_file_name + '.dat'
    if False == os.path.exists(db_file):
        return last_update_time, None
    with open(db_file, 'rb') as f:
        last_update_time = pickle.load(f)
        data = pickle.load(f)
    return last_update_time, data


def db_get_data_fold():
    home = os.getenv('HOME')
    path = home + '/.cache/' + DATA_FOLD + '/'
    if False == os.path.exists(path):
        os.makedirs(path)
        print('create fold {}'.format(path))
    return path
