def splitBigFile(src:str, dest:str, encoding:str = 'utf-8'):
    with open(src, 'r', encoding=encoding) as fr:
        lineNum = 0
        fileNum = 0
        lines = []
        while 1:
            if lineNum < 100000:
                line = fr.readline()
                if not line:
                    if lineNum == 0:
                        return
                    else:
                        with open(dest+'/split_file_'+str(fileNum)+'.txt', 'w', encoding=encoding) as fw:
                            fw.writelines(lines)
                        return
                else:
                    lines.append(line)
                    lineNum += 1
            else:
                with open(dest+'/split_file_'+str(fileNum)+'.txt', 'w', encoding=encoding) as fw:
                    fw.writelines(lines)
                lineNum = 0
                fileNum += 1
                lines = []