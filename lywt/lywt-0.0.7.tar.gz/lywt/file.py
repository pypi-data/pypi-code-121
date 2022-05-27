def splitBigFile(src: str, dest: str, encoding: str = 'utf-8'):
    lineNum = 0
    fileNum = 0
    lines = []
    with open(src, 'r', encoding=encoding) as fr:
        for line in fr.readlines():
            lines.append(line)
            lineNum += 1
            if lineNum == 100000:
                with open(dest+'/split_file_'+str(fileNum)+'.txt', 'w', encoding='utf-8') as fw:
                    for line in lines:
                        fw.write(line)
                    fileNum += 1
                    lineNum = 0
                    lines = []
    with open(dest+'/split_file_'+str(fileNum)+'.txt', 'w', encoding='utf-8') as fw:
        for line in lines:
            fw.write(line)
