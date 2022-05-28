# This app is ONLY used for formatting source.excel's data
import xlsxwriter
from copy import deepcopy
from source.comment import comment
from source.formatdefinition import special_format, COLUMN_WIDTH, VALUE_FORMAT, TITLE_FORMAT, DESCRIPTION_FORMAT, COLUMN_TITLE_FORMAT, VARIABLE_TITLE_FORMAT, COMMENT_FORMAT
from importlib import import_module

# from source.validation import validation
validation=import_module("source.validation").validation

class ExcelWritter():
    def __init__(self, input_excel_obj, out_excel):
        self.workbook = xlsxwriter.Workbook(
            out_excel, {'default_date_format': "yyyy-mm-dd"})
        self.workbook.set_size(1440, 1640)
        self.excel = deepcopy(input_excel_obj)
        self.protection_options = {
            'objects':               False,
            'scenarios':             False,
            'format_cells':          False,
            'format_columns':        True,
            'format_rows':           True,
            'insert_columns':        False,
            'insert_rows':           False,
            'insert_hyperlinks':     False,
            'delete_columns':        False,
            'delete_rows':           False,
            'select_locked_cells':   False,
            'sort':                  False,
            'autofilter':            False,
            'pivot_tables':          False,
            'select_unlocked_cells': True,
        }

    def _createTitle(self, worksheet, title, column_number):
        format = self.workbook.add_format(TITLE_FORMAT)
        worksheet.merge_range(0, 0, 0, column_number-1, None, format)
        worksheet.write(0, 0, title, format)

    def _createColumnTitles(self, worksheet, titles):
        for index, title in enumerate(titles):
            format = self.workbook.add_format(COLUMN_TITLE_FORMAT)
            worksheet.write(1, index, title, format)

    def _createColumnVariables(self, worksheet, variables):
        for index, variable in enumerate(variables):
            format = self.workbook.add_format(COLUMN_TITLE_FORMAT)
            worksheet.write(2, index, variable, format)
        worksheet.set_row(2, 0, self.workbook.add_format({"hidden": True}))

    def _createSheetContents(self, worksheet, sheetcontent, sheet_name):
        # 获得所有variable, tag, description, and value
        row = 3  # initial row is 3
        for row_obj in sheetcontent.data.values():
            worksheet.write(row, 0, row_obj.variable)
            worksheet.write(row, 1, row_obj.tag)
            worksheet.write(row, 2, row_obj.description,
                            self.workbook.add_format(DESCRIPTION_FORMAT))
            # write value with special format and default foramt
            if sheet_name in special_format.keys() and row_obj.variable in special_format[sheet_name] and special_format[sheet_name][row_obj.variable]:
                new_format = self.workbook.add_format(
                    {**VALUE_FORMAT, **special_format[sheet_name][row_obj.variable]})
            elif "_date" in row_obj.variable:
                new_format = self.workbook.add_format({
                    **VALUE_FORMAT, **{'num_format': 'yyyy-mm-dd'}})
            else:
                new_format = self.workbook.add_format(VALUE_FORMAT)
            worksheet.write(row, 3, row_obj.value, new_format)

            # add comment
            if sheet_name in comment.keys() and row_obj.variable in comment[sheet_name] and comment[sheet_name][row_obj.variable]:
                worksheet.write_comment(
                    row, 2, comment[sheet_name][row_obj.variable], COMMENT_FORMAT)

            # add data validation
            if sheet_name in validation.keys() and row_obj.variable in validation[sheet_name] and validation[sheet_name][row_obj.variable]:
                worksheet.data_validation(
                    row, 3, row, 3, validation[sheet_name][row_obj.variable])

            row += 1

    def _createTableContents(self, worksheet, tablecontent):
        table_name = "table-"+tablecontent.name
        # 获得所有table data and write
        r = 3
        for row in tablecontent.data:
            c = 0

            # Iterate over the data and write it out row by row.
            for variable, value in row.__dict__.items():
                if "_date" in variable:
                    new_format = self.workbook.add_format(
                        {**VALUE_FORMAT, **{'num_format': 'yyyy-mm-dd'}})
                elif table_name in special_format.keys() and variable in special_format[table_name] and special_format[table_name][variable]:
                    new_format = self.workbook.add_format(
                        {**VALUE_FORMAT, **special_format[table_name][variable]})
                else:
                    new_format = self.workbook.add_format(VALUE_FORMAT)
                worksheet.write(
                    r, c, value, new_format)
                c += 1
            c = 0
            r += 1

    def createSheet(self, protection, password):
        # 获取所有sheet表，column titles, column variables
        for sheet, sheetcontent in self.excel.sheets.items():
            sheet_name = 'info-'+sheet
            worksheet = self.workbook.add_worksheet(sheet_name)
            # create sheet
            self._createTitle(worksheet, self.excel.sheets[sheet].sheet_title, len(
                self.excel.sheets[sheet].column_variables))
            self._createColumnTitles(
                worksheet, self.excel.sheets[sheet].column_titles)
            self._createColumnVariables(
                worksheet, self.excel.sheets[sheet].column_variables)
            self._createSheetContents(worksheet, sheetcontent, sheet_name)
            # format sheet in sheet level
            worksheet.set_column(
                'A:B', 15, None, {'hidden': True})
            worksheet.set_column(
                'C:C', 70, None, {'text_wrap': True})
            worksheet.set_column(
                'D:D', 70, None, {'text_wrap': True})
            # protect the sheet
            if protection:
                worksheet.protect(password, self.protection_options)

    # 获取所有table表 column titles, column variables
    def createTable(self, protection, password):
        for table, tablecontent in self.excel.tables.items():
            table_name = 'table-'+table
            worksheet = self.workbook.add_worksheet(table_name)
            variables = tablecontent.column_variables
            titles = [tablecontent.column_titles[x]
                      for x in variables]
            # create table
            self._createTitle(
                worksheet, self.excel.tables[table].sheet_title, len(variables))
            self._createColumnTitles(worksheet, titles)
            self._createColumnVariables(worksheet, variables)
            self._createTableContents(worksheet, tablecontent)
            # format table in sheet level
            for index, variable in enumerate(variables):

                # 2. set date format
                if "_date" in variable:
                    the_format = self.workbook.add_format(
                        {'num_format': 'yyyy-mm-dd', 'align': "center"})
                    worksheet.set_column(index, index, 12, the_format)
                # 3. add validation
                if table_name in validation.keys() and variable in validation[table_name] and validation[table_name][variable]:
                    worksheet.data_validation(
                        3, index, 303, index, validation[table_name][variable])
                # 4. add comment
                if table_name in comment.keys() and variable in comment[table_name] and comment[table_name][variable]:
                    worksheet.write_comment(
                        1, index, comment[table_name][variable], COMMENT_FORMAT)
                # 5. set column with special format and default foramt
                if table_name in special_format.keys() and variable in special_format[table_name] and special_format[table_name][variable]:
                    new_format = self.workbook.add_format(
                        {**VALUE_FORMAT, **special_format[table_name][variable], "border": 0})
                else:
                    new_format = self.workbook.add_format(
                        {**VALUE_FORMAT, "border": 0})
                # set column width
                if variable in COLUMN_WIDTH.keys():
                    worksheet.set_column(
                        index, index, COLUMN_WIDTH[variable], new_format)
                else:
                    worksheet.set_column(index, index, 15, new_format)
            # protect the sheet
            if protection:
                worksheet.protect(password, self.protection_options)

    def create(self, protection=True, password=""):
        self.createSheet(protection, password)
        self.createTable(protection, password)
        self.workbook.close()

# e=Excel("/Users/jacky/desktop/doc/all.xlsx")
# ew = ExcelWritter(e,"/Users/jacky/desktop/a.xlsx")
# ew.create(protection=True, password="111")
