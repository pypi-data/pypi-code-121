from ipaddress import ip_address
from os.path import basename
from pathlib import Path

''' 函数内部变量, 变量名一律以 _ (下划线) 开头, 避免改变上层相同名称的变量 '''

def nums_mam(numbers=[], type=None):
    ''' 返回一组数字中的 最大值, 平均值, 最小值 '''
    _num_max, _num_avg, _num_min = None, None, None
    try:
        if len(numbers) > 0:
            if type == 'int':
                numbers = [int(i) for i in numbers]
            if type == 'float':
                numbers = [float(i) for i in numbers]
            _num_max = max(numbers)
            _num_avg = sum(numbers) / len(numbers)
            _num_min = min(numbers)
            return _num_max, _num_avg, _num_min
    except Exception as e:
        print(e)
        return _num_max, _num_avg, _num_min

def stat_is(target='', type='file'):
    ''' 检查目标类型 (默认: file) '''
    try:
        _stat = Path(target)
        match True:
            case True if type == 'absolute' and _stat.exists() and _stat.is_absolute():
                return True
            case True if type == 'block_device' and _stat.exists() and _stat.is_block_device():
                return True
            case True if type == 'dir' and _stat.exists() and _stat.is_dir():
                return True
            case True if type == 'fifo' and _stat.exists() and _stat.is_fifo():
                return True
            case True if type == 'file' and _stat.exists() and _stat.is_file():
                return True
            case True if type == 'mount' and _stat.exists() and _stat.is_mount():
                return True
            case True if type == 'relative_to' and _stat.exists() and _stat.is_relative_to():
                return True
            case True if type == 'reserved' and _stat.exists() and _stat.is_reserved():
                return True
            case True if type == 'socket' and _stat.exists() and _stat.is_socket():
                return True
            case True if type == 'symlink' and _stat.exists() and _stat.is_symlink():
                return True
            case _:
                return False
    except:
        return False

def list_sort_by_ip(ips=[], deduplication=True):
    ''' 排序, 去重 '''
    try:
        _ips_ipaddress = sorted(ip_address(ip.strip()) for ip in ips)
        _ips_string = [str(i) for i in _ips_ipaddress]
        if deduplication:
            return list(set(_ips_string))
        else:
            return _ips_string
    except Exception as e:
        print(e)
        return []

def filename(file='', split='.'):
    '''
    获取文件名
    https://stackoverflow.com/questions/678236/how-do-i-get-the-filename-without-the-extension-from-a-path-in-python
    https://stackoverflow.com/questions/4152963/get-name-of-current-script-in-python
    '''
    try:
        _basename = basename(file)
        _index_of_dot = _basename.index(split)
        return _basename[:_index_of_dot]
    except:
        return Path(file).stem
