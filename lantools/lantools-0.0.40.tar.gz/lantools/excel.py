from openpyxl import Workbook

class Excel:
    @classmethod
    def save_excel(cls, filename, data):
        # 实例化
        wb = Workbook()
        # 激活 worksheet
        ws = wb.active
        ws.title = "sheet1"

        i = 1
        for row in data:
            column=0

            if type(row)==dict:
                array = row.values()
            else:
                array = row

            for value in array:
                ws[chr(65+column)+str(i)] = value
                column += 1

            i += 1

        wb.save(filename)