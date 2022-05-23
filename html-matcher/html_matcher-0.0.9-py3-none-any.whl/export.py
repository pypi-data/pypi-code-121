import xlsxwriter as xw
import os

class ExcelExporter(object):

    def __init__(self, data, details, duration, offset, offset_increment, method, website, nr_files):
        self.data = data
        self.details = details
        self.duration = duration
        self.offset = offset
        self.offset_increment = offset_increment
        self.method = method
        self.website = website
        self.nr_files = nr_files

    def results_to_excel(self):
        self.__build_file()

        self.__build_table_header(0)

        self.__build_table_body(0)

        self.__build_graphics()

        self.__build_details()

        self.file.close()

        print(f"Exported: {self.file.filename}")

    def __build_file(self):
        if not os.path.exists(self.website):
            os.mkdir(self.website)
        self.file = xw.Workbook(f'{self.website}/{self.method}_{self.website}_{self.nr_files}.xlsx')
        self.page = self.file.add_worksheet('Results')

    def __build_table_header(self, row):
        self.page.write(row, 0, "Method")
        self.page.write(row, 1, "Threshold")
        self.page.write(row, 2, "TP")
        self.page.write(row, 3, "TN")
        self.page.write(row, 4, "FP")
        self.page.write(row, 5, "FN")
        self.page.write(row, 6, "Sensitivity")
        self.page.write(row, 7, "Specificity")
        self.page.write(row, 8, "FP Rate")
        self.page.write(row, 9, "FN Rate")
        self.page.write(row, 10, "Youden Index")
        self.page.write(row, 11, "Accuracy")

        merge_format = self.file.add_format({'align': 'center', 'valign': 'vcenter'})
        self.page.merge_range('A2:A22', self.method, merge_format)

    def __build_table_body(self, row):
        split_size = 4
        aux_data = [self.data[x:x + split_size] for x in range(0, len(self.data), split_size)]
        aux_offset = self.offset
        for value in aux_data:
            row += 1

            self.page.write(row, 1, aux_offset)
            self.page.write(row, 2, value[0])
            self.page.write(row, 3, value[1])
            self.page.write(row, 4, value[2])
            self.page.write(row, 5, value[3])
            self.page.write(row, 6, f"=C{row + 1}/(C{row + 1}+F{row + 1})")
            self.page.write(row, 7, f"=D{row + 1}/(D{row + 1}+E{row + 1})")
            self.page.write(row, 8, f"=E{row + 1}/(E{row + 1}+D{row + 1})")
            self.page.write(row, 9, f"=F{row + 1}/(F{row + 1}+C{row + 1})")
            self.page.write(row, 10, f"=G{row + 1}+H{row + 1}-1")
            self.page.write(row, 11, f"=(C{row + 1}+D{row + 1})/(C{row + 1}+D{row + 1}+E{row + 1}+F{row + 1})")

            aux_offset += self.offset_increment

    def __build_graphics(self):
        chart = self.file.add_chart({'type': 'line'})

        chart.add_series({'name': '=Results!$C$1', 'values': '=Results!$C$2:$C$22', 'marker': {'type': 'circle'},
                          'categories': '=Results!$B$2:$B$22'})
        chart.add_series({'name': '=Results!$D$1', 'values': '=Results!$D$2:$D$22', 'marker': {'type': 'circle'}})
        chart.add_series({'name': '=Results!$E$1', 'values': '=Results!$E$2:$E$22', 'marker': {'type': 'circle'}})
        chart.add_series({'name': '=Results!$F$1', 'values': '=Results!$F$2:$F$22', 'marker': {'type': 'circle'}})

        chart.set_x_axis({'name': '=Results!$B$1'})

        self.page.insert_chart('N2', chart)

        chart = self.file.add_chart({'type': 'line'})

        chart.add_series({'name': '=Results!$G$1', 'values': '=Results!$G$2:$G$22', 'marker': {'type': 'circle'},
                          'categories': '=Results!$B$2:$B$22'})
        chart.add_series({'name': '=Results!$H$1', 'values': '=Results!$H$2:$H$22', 'marker': {'type': 'circle'}})

        chart.set_x_axis({'name': '=Results!$B$1'})

        self.page.insert_chart('N17', chart)

    def __build_details(self):
        self.page.write(24, 0, "Duartion: " + str(self.duration))
        for row, line in enumerate(self.details):
            for col, cell in enumerate(line):
                self.page.write(row + 25, col, cell)
