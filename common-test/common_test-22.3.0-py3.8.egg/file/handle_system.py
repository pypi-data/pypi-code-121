import os
from common.config.config import CONFIG_PATH, TEST_DATA_PATH


def make_path(pathdir: str):
    """
    创建文件夹，如果当前文件夹存在不创建，反之创建
    :param pathdir: 路径
    :return:
    """
    IsExists = os.path.exists(adjust_path(pathdir))
    # 如果不存在，则创建文件夹
    if IsExists == False:
        os.makedirs(adjust_path(pathdir))
    return adjust_path(pathdir)

def adjust_path(path):
    """根据操作系统转换文件分隔符
    """
    if os.sep == '/':
        return path.replace('\\', os.sep)
    else:
        return path.replace('/', os.sep)

def adjust_path_data(_path):
    """是否自动加入data
    """
    if TEST_DATA_PATH in _path:
        _path = _path
    else:
        _path = os.path.join(TEST_DATA_PATH, _path, )
    return adjust_path(_path)


def get_resource(relative_path: str):
    """
    @params relative_path: 从resource目录级开始的文件相对路径
    例如： ad_batch_info_add.json
    return: 返回绝对路径
    """
    """根据操作系统转换文件分隔符
    """
    relative_path = adjust_path(relative_path)
    resource_paths = []
    for dirpath, dirnames, _ in os.walk(CONFIG_PATH):
        for dirname in dirnames:
            if dirname == 'resource':
                resource_paths.append(os.path.join(dirpath, dirname))
    found_paths = []
    for it in resource_paths:
        file_path = adjust_path(os.path.join(it, relative_path))

        if os.path.exists(file_path):
            found_paths.append(file_path)
    if len(found_paths) == 0:
        raise Exception("relative_path=%s not found" % relative_path)
    if len(found_paths) > 1:
        raise Exception("relative_path=%s got multiple results:\n%s" % (relative_path, "\n".join(found_paths)))
    return os.path.abspath(found_paths[0])

def  del_file(path):
      """
      删除所有文件(保护里面文件夹）
      :param path:
      :return:
      """
      for i in os.listdir(path):
         path_file = os.path.join(path,i)
         if os.path.isfile(path_file):
           os.remove(path_file)
         else:
             del_file(path_file)
