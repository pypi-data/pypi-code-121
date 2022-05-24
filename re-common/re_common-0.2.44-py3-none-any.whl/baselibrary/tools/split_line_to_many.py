"""
一行文本按指定符号分割为多行文本
"""


class Split_2_lines(object):
    def __int__(self):
        pass

    def split_line(self, infilepath, sign, outfilepath=None):
        """
        :param infilepath: 输入文件位置
        :param sign: 分割符号
        :param outfilepath: 输出文件位置
        :return:
        """
        with open(infilepath, 'r', encoding='utf-8')as f:
            for line in f:
                list_ = line.split(sign)[:-1]
                for num in list_:
                    new_line = num + sign + "\n"
                    with open(outfilepath, 'a', encoding='utf-8')as fw:
                        fw.write(new_line)
                        print(new_line)
        print("输出{}成功".format(outfilepath))
