from convert_xmind_to_excel import ConvertXmindToExcel
import sys


if __name__ == '__main__':
    # xmind_file_path = '/Users/xu.nie/Documents/基线用例整理文档/MbsdCore_1300_790000_统一冲正.xmind'
    # excel_file_path = '/Users/xu.nie/Documents/test.xlsx'
    # ignore_layer_number = 1
    # para_list = ['/Users/xu.nie/Desktop/端到端用例编写.xmind', '/Users/xu.nie/Desktop/test.xlsx']
    para_list = sys.argv[1:]
    if len(para_list) == 3:
        ConvertXmindToExcel().convert(para_list[0], para_list[1], ignore_layer_number=para_list[2])
    else:
        ConvertXmindToExcel().convert(para_list[0], para_list[1])
    sys.exit()