import xlrd

def read_excel(file_path, sheet_name):
    # 读取Excel表格数据
    workxls = xlrd.open_workbook(file_path)
    worksheet = workxls.sheet_by_name(sheet_name)
    row = worksheet.nrows  # 总行数
    # print("Excel行数：{}".format(row))
    return worksheet, row

def obtainexcelinfo(filePath, sheetName):
    workSheet, rows = read_excel(filePath, sheetName)
    keys = workSheet.row_values(0)
    data_list=[]
    for row in range(1, rows):
        rowData = workSheet.row_values(row)
        item = dict(zip(keys, rowData))
        data_list.append(item)
    return data_list