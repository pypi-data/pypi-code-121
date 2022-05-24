import xlsxwriter
import pandas as pd
import os


class excel_format:
    """
    Excel Format class help to create customized format excel file.
    """

    def __init__(self, path=os.getcwd(), output_name="reports.xlsx"):
        self.output_name=output_name
        self.path = path
        ## create a workbook with a given name
        self.writer=pd.ExcelWriter(os.path.join(self.path,self.output_name),
                                engine="xlsxwriter")
        self.workbook=self.writer.book

        
    def convert_csv_to_xlsx(self,file_path,custom_sheet_name=None):
        """
        This function will take the data from CSV file in the folder
        Converting CSV file into a data frame
        Return workbook and worksheet for further manipulation

        """
        self.data_frame = pd.read_csv(file_path, encoding='utf-8',index_col=False)

        self.row_length, self.column_length = self.data_frame.shape

        split_value=str(file_path).split("/")

        sheet_name=None
        if custom_sheet_name==None:
            sheet_name=split_value[-1].replace(".csv","")
        else:
            sheet_name=custom_sheet_name

                
        self.data_frame.to_excel(self.writer, index=False, sheet_name=sheet_name)
        

        self.worksheet = self.writer.sheets[sheet_name]
        
        

    def row_rotation(self, row, angle):
        """
        This function will rotate the row.
        :param row: Row Index Represent in Int
        :param angle: The degree that you want to rotate. Takes in Int
        :return:
        """
        if row == 0:
            row_data = self.data_frame.columns.tolist()
            row_data = [str(data).replace("nan", "") for data in row_data]
        else:
            row_data = self.data_frame.iloc[row].tolist()
            row_data = [str(data).replace("nan", "") for data in row_data]
        format = self.workbook.add_format()
        format.set_rotation(angle)

        tuple_row_data = tuple(row_data)

        self.worksheet.write_row(0, 0, tuple_row_data, format)

    def row_format(self, row, height, format=None):

        """
        This function provides custom format for the entire row.

        :param row:  Integer
        :param height: Integer
        :param format: workbook Format
        :return:
        """
        if format != None:
            format = self.workbook.add_format(format)
        self.worksheet.set_row(row, height, format)

    def freeze_panel(self, column, row):
        """
        This will freeze the pannel
        :param column: Int
        :param row: Int
        :return:
        """
        self.worksheet.freeze_panes(column, row)

    def autofilter_whole_sheet(self):
        """
        Run this function will create a filter for the whole sheet
        :return:
        """

        self.worksheet.autofilter(0, 0, self.row_length, self.column_length - 1)

    def get_column_index(self, column_name):
        """
        This function return the index given column name
        :param column_name: String
        :return: Integer
        """
        column_names = self.data_frame.columns.tolist()
        index = None

        for inde, name in enumerate(column_names):
            if name == column_name:
                index = inde
        return int(index)

    def condition_format_column(self, column_name, formats=None):
        """
        This provides conditional formatting for column
        :param column_name: String
        :param formats: Workbook Format
        :return:
        """
        index = self.get_column_index(column_name)

        for format in formats:
            self.worksheet.conditional_format(1, index, self.row_length, index, format)

    def num_format(self, column_name, format=None):
        """
        This function provides formatting for number

        :param column_name: String
        :param format: Work book format
        :return:
        """
        json_format = {
            'num_format': f"{format}"
        }
        format = self.workbook.add_format(json_format)
        index = self.get_column_index(column_name)
        self.worksheet.set_column(index, index, None, format)

    def set_column_width(self, column_name, column_width):
        """
        This function sets up the width column.
        :param column_name: String

        :param column_width: Integer
        :return:
        """
        index = self.get_column_index(column_name)
        self.worksheet.set_column(index, index, column_width)

    def column_width_size_set(self,column_name,pixel):
        index=self.get_column_index(column_name)
        self.worksheet.set_column_pixels(index,index,pixel)

    def column_width_auto_size(self, column_name, include_header=True):
        """
        This function will automatically adjust your columns width size
        :param column_name: String
        :return:
        """
        
        data = self.data_frame[column_name].tolist()
        if include_header==True:
            data.append(column_name)
        else:
            pass
        

        data = [str(i).replace("nan", ",") for i in data]

        len_list = [len(str(i)) for i in data]

        max_len = max(len_list)

        character_value = data[len_list.index(max_len)]

        lower_case_char = 0
        uper_case_char = 0
        for char in character_value:
            if char.isupper():
                uper_case_char += 1
            else:
                lower_case_char += 1

        index = self.get_column_index(column_name)
        pixl_value = (90 / 10) * uper_case_char + (80 / 10) * lower_case_char
        self.worksheet.set_column_pixels(index, index, pixl_value)

    def column_data_validation(self, column_name, list):
        """
        This functions provides Excel Validation given list and column name
        :param column_name: String
        :param list: List
        :return:
        """
        validation_json = {
            'validate': 'list',
            'source': list
        }
        index = self.get_column_index(column_name)
        self.worksheet.data_validation(1, index, self.row_length, index, validation_json)

    def no_repeat(self, list):
        """
        This functions remove repeated items in a list
        :param list: list
        :return:
        """
        no_repeated_list = []
        for item in list:
            if item not in no_repeated_list:
                no_repeated_list.append(item)
        return no_repeated_list

    def get_category(self, column_name):
        """
        This function will return set of category in a column with no repeated value
        :param column_name:String
        :return: List
        """

        category_list = self.data_frame[column_name].tolist()
        return self.no_repeat(category_list)

    def category_color_format_generator(self, item_list, color_list, string=True):
        """
        This functions generating a json data for workbook formatting given Item List and Color List
        :param item_list:List
        :param color_list: List
        :param string: Optional whether data is string or int
        :return: Json Object. Workbook Formatting
        """
        format_array = []
        zip_list = zip(item_list, color_list)
        for item, color in zip_list:
            color_format = self.workbook.add_format({"bg_color": color})
            if string == True:

                json_format = {
                    "type": "cell",
                    "criteria": "equal to",
                    "value": f"\"{item}\"",
                    "format": color_format
                }
            else:
                json_format = {
                    "type": "cell",
                    "criteria": "equal to",
                    "value": f"{item}",
                    "format": color_format
                }
            format_array.append(json_format)
        return format_array

    # def combine(self):
    #     formatD={'type': '3_color_scale',
    #                                  'min_color': "red",
    #                                  'mid_color': "yellow",
    #                                  'max_color': "green"}
    #     formats=[formatD]
    #     grey=self.workbook.add_format({'bg_color':'red'})
    #     formatA={'type': 'cell',
    #                 'criteria':'equal to',
    #                 'value': '"TERM_OF_INTEREST"',
    #                 'format':grey
    #              }
    #     formats1=[formatA]
    #     contitional_format={'type':'3_color_scale','min_color': '#C5D9F1',
    #                                     'max_color': '#538ED5'}
    #
    #     self.condition_format_column("frequency_percentile",formats)
    #     self.condition_format_column("system_asserted_tag", formats1)
    #     self.freeze_panel(1,1)
    #     self.row_format(1,50)
    #     self.row_rotation(0,30)
    #     self.autofilter_whole_sheet()
    #     self.workbook.close()


"""
needed function documentation
set_column()
set_rotation(angle)
worksheet.set_row()
"""



