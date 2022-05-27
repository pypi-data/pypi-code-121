# coding:utf-8

import glob

"""
获取当前路径下所有内容
判断每个内容的类型（文件夹还是文件）
若是文件夹则继续递归查找
"""

path =  # 因为下文捕获不可读文件格式太多，所以这里直接指定了 "test04" 路径


def search(search_path, content):  # 定义 search() 函数，传入 "path" 文件路径， "target" 要查找的目标文件
    glob_path = glob.glob(search_path)

    for file_path in glob_path:  # for 循环判断递归查到的内容是文件夹还是文件
        if glob.os.path.isdir(file_path):  # 若是文件夹，继续将该文件夹的路径传给 search() 函数继续递归查找
            _path = glob.os.path.join(file_path, '*')
            search(_path, content)
        else:  # 若是文件，则将该查询到的文件所在路径插入 final_result 空列表
            try:
                f = open(file_path, 'r')  # 利用 open() 函数读取文件，并通过 try...except... 捕获不可读的文件格式（.zip 格式）
                file_content = f.read()
                if content in file_content:
                    print(file_path)

            except:
                continue
            finally:
                f.close()


if __name__ == '__main__':
    result = search(r'D:\work\BaiduNetdiskWorkspace\personal' , content='runserver')
    # print(result)
