
def read_lines(filename, strip=False):
    # 打开文件
    fo = open(filename, "r")
    
    result =[]
    for line in fo.readlines():
        if strip==True:
            line = line.strip()

        result.append(line)
    
    # 关闭文件
    fo.close()

    return result