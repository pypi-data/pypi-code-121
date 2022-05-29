"""
My_db - class for working with own database

How to use?
1. init db by providing path to txt file
2. use read method to read db
3. now can be used with different api methods
4. when manipulation completed do not forget to save db

Nb. If required to use db methods without 'path' pass 'data' object which should be the same
as db.__hash_value(same format)

1.  my_db = db(path, data=None)
2.  db.read()
3.  db.add({data:'new'})
4.  db.save()

Notes if db file do not exist it will be crated automatically. At his point it is recommended to use read method any way

API REF
    Class methods which can be private:
    db.read() - method converts files data to hash_table which is going to be used inside the class method used
    inside the class during init

    db.format_data() - method creates from __hash_values nicely formatted data which is going to be stored in text file
        retunr self and when completed self.__formatted_data is going to store all formated text

    db.rebuilt_sorted_dict() - method which is build from sorted data db data

    APi metods
    db.get_data() - method return a full hash_table of the db class

    db.add(row) - method for adding new entries to db
                -takes dictionary as an argument with key and value
                - key will be used as label in formatted data when save db
                - during init it adds data to db by using __cur_hash value to add it to __hash_values
    db.save() - method which saves data to the file. Nb use everytime at the end of the script or work

    db.delete_by_index(index) - method for deleting entries from db by using index

    db.sort_by(category, is_float_base = False, is_reverse = True)
                            - method which sorts db data by using category name as a flag/indicator
                            - by default sorted higher first lower last
                            - if category do not present in some objects they will be passed
                            - return sorted hash-table with required category
                            - by default is_float_base = False it means it is sorting content as a string
                            it can be used with pairs of numbers which can be converted from string to the float
                            NB!! if number has ',' inside is_float_base will through an error cause it can not
                            convert to the number. Good - '131.2312' Bad - '12312,122'
                            - is_reverse by default is true. if change to false it will sort in opposite way.

    db.find_by_index(index) - method allows finding object/row from db by its index
                            - return full object/row

    db.find_objects(category_name) - method which returns a hash with indexes and categories values

    db.get_position(pattern)    - method which uses pattern to find first match in db
                                - return first found match object index, if not found return 0

    db.get_obj_by_pattern(pattern) - method return first object with found pattern as an object {}

    db.get_all_cat_values(category) - method return all values of the match category as a list

    db.find_objs_where_value_match(category, value) - method which returns a list with objects
    which matches with required value in category

    db.find_all_objs_by_pattern(pattern) - method which returns all rows witch match with pattern.
                                            if not found return {}

    db.check_if_exists(pattern) - method return boolean True if pattern present otherwise False

    db.filter_all_queries(patterns_arr) - method return a hash with all results of passed queries
                                        -patterns_arr - an array with valid queries

    db.get_filtered_object() - this method return TextDb object where data equals to the
                            latest results of filter_all_queries(patterns_arr) method
                            Why this method exists? After a while I found out that I want to sort the filtered data
                            but to achieve this goal I had to write the same code again somewhere else. Of course, it
                            was a bad solution. So I came up with idea of this method. This allows me to use all methods
                            from this class if needed.

    db.filter_by_almost_equal(category_name, arr_of_values) - this method returns a hash where category values almost
                            equal to the arr_of_values.
                            Nb! use this method if category  has coma separated values. <cat>'1,2'<cat>
                            or <cat>'s,x,m'<cat>
                            Basically it checks if values
                            of one arr present in the second arr if so add to filtered_object.




static methods

    extract_flag(data_row) - > method allow extracting flag from the row - > <cat>name<cat> return <cat>
    extract_flag_value(flag) -> method allow extracting value from the flag
    extract_value(flag) -> allow extract value from flag tags -> <cat>name<cat> return <cat> return name
    extract_key_and_value(data_row) -> combination of prev methods -> <cat>name<cat> return  [cat, name]
    check_is_row_valid(row) -> checks if the row is a dict return True or raise exception
    extract_range(value) -> extracts start and finish values from value. if value has '-' split it abd return
        float numbers of the values [start,finish]
        If value is single return [0, finish]
"""


class TextDb:

    @staticmethod
    def extract_flag(data_row):
        flag_end = '>'
        flag = ''
        for char in data_row:
            if char == flag_end:
                flag += char
                break
            flag += char
        return flag

    @staticmethod
    def extract_flag_value(flag):
        return flag.replace('<', '').replace('>', '')

    @staticmethod
    def extract_value(data_row, flag):
        return data_row.replace(flag, '')

    @staticmethod
    def extract_key_and_value(data_row):
        # flag value is a key
        flag = TextDb.extract_flag(data_row)
        return [TextDb.extract_flag_value(flag), TextDb.extract_value(data_row, flag)]

    @staticmethod
    def check_is_row_valid(row):
        if type(row) is dict:
            return True
        raise ValueError(f'Expected dictionary but received {type(row)}')

    @staticmethod
    def extract_range(value):
        if '-' in value:
            start, end = value.split('-')
            return [float(start), float(end)]
        return [0, float(value)]

    def __init__(self, db_path, data=None):
        self.db_path = db_path
        self.__data_obj_flag = '<Item>'
        self.__index = 0
        self.__hash_values = {}
        self.__cur_hash = {}
        self.__formatted_data = ''
        self.sorted_dict = None
        self.latest_sorted_data = None
        self.filtered_queries = None

        if isinstance(data, dict):
            self.__hash_values = data
        else:
            try:
                with open(db_path, 'r') as file:
                    data = [line.strip() for line in file.readlines()]
                    self.read(data)
            except FileNotFoundError:
                print('File not found')
                with open(db_path, 'a') as _:
                    self.__hash_values = {}
                print('New db created')

    def read(self, data):
        cur_item = False
        for line in data:
            if line == self.__data_obj_flag:
                if cur_item:
                    self.add(self.__cur_hash)
                    self.__cur_hash = {}
                    cur_item = False
                else:
                    cur_item = True
            else:
                key, value = TextDb.extract_key_and_value(line)
                self.__cur_hash[key] = value
        return self

    def get_data(self):
        return self.__hash_values

    def add(self, row):
        TextDb.check_is_row_valid(row)
        self.__index += 1
        self.__hash_values[self.__index] = row
        return self

    def format_data(self):
        self.__formatted_data = ''
        for key in self.__hash_values.keys():
            self.__formatted_data += '<Item>\n'
            for col in self.__hash_values[key].keys():
                value = self.__hash_values[key][col]
                self.__formatted_data += f'\t<{col}>{value}<{col}>\n'
            self.__formatted_data += '<Item>\n'
        return self

    def save(self):
        self.format_data()
        with open(self.db_path, 'w') as file:
            file.write(self.__formatted_data)

    def delete_by_index(self, index):
        if self.__hash_values.get(index):
            self.__hash_values.pop(index)
            return
        return

    def find_objects(self, category):
        objs_with_cat = {}
        for index in self.__hash_values:
            if category in self.__hash_values[index]:
                objs_with_cat[index] = self.__hash_values[index][category]

        return objs_with_cat

    def rebuilt_sorted_dict(self):
        if not self.sorted_dict:
            return {}
        return {index: self.__hash_values[index] for index, _ in self.sorted_dict}

    def sort_by(self, category, is_reverse=True, is_float_base=False):

        objs_with_cat = self.find_objects(category)
        if is_float_base:
            self.sorted_dict = sorted(objs_with_cat.items(), key=lambda x: float(x[1]), reverse=is_reverse)
            return self.rebuilt_sorted_dict()
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value
        self.sorted_dict = sorted(objs_with_cat.items(), key=lambda x: x[1], reverse=is_reverse)
        self.latest_sorted_data = self.rebuilt_sorted_dict()
        return self.latest_sorted_data

    def find_by_index(self, index):
        return self.__hash_values[index]

    def get_position(self, pattern):
        TextDb.check_is_row_valid(pattern)
        keys = list(pattern)
        first_key = keys[0]
        key_qty = len(keys)
        # pattern key should be the same as in db if not found return 0
        for index, obj in self.__hash_values.items():
            brake_flag = None
            if first_key in obj:
                if key_qty > 1:
                    for key in keys:
                        if key not in obj or obj[key] != pattern[key]:
                            brake_flag = True
                            break
                    if not brake_flag:
                        return index
                elif obj[first_key] == pattern[first_key]:
                    return index
        return 0

    def get_obj_by_pattern(self, pattern):
        position = self.get_position(pattern)
        return self.find_by_index(position)

    def get_objs_where_value_match(self, category, value):
        found = []
        objects = self.find_objects(category)
        for index, obj_value in objects.items():
            if value == obj_value:
                found.append(self.find_by_index(index))

        return found

    def get_formatted_data(self):
        return self.__formatted_data

    def get_all_cat_values(self, category):
        return list(self.find_objects(category).values())

    def get_indexes(self, pattern):
        TextDb.check_is_row_valid(pattern)
        found = []
        keys = list(pattern)
        first_key = keys[0]
        key_qty = len(keys)
        # pattern key should be the same as in db if not found return 0
        for index, obj in self.__hash_values.items():
            brake_flag = None
            if first_key in obj:
                if key_qty > 1:
                    for key in keys:
                        if key not in obj or obj[key] != pattern[key]:
                            brake_flag = True
                            break
                    if not brake_flag:
                        found.append(index)
                elif obj[first_key] == pattern[first_key]:
                    found.append(index)
        return found

    def find_all_objs_by_pattern(self, pattern):
        found_indexes = self.get_indexes(pattern)
        if len(found_indexes) >= 1:
            return {index: self.find_by_index(index) for index in found_indexes}
        return {}

    def check_if_exists(self, pattern):
        return self.get_position(pattern) != 0

    def filter_all_queries(self, patterns_arr):
        self.filtered_queries = {}
        for query in patterns_arr:
            found_data = self.find_all_objs_by_pattern(query)
            self.filtered_queries.update(found_data)
        return self.filtered_queries

    def get_filtered_object(self):
        if isinstance(self.filtered_queries, dict):
            return TextDb('_', data=self.filtered_queries)
        return None

    def filter_by_range(self, category_name, range_value):
        min_val, max_val = TextDb.extract_range(range_value)
        self.filtered_queries = {}
        for index, values in self.__hash_values.items():
            if category_name in values:
                cur_value = float(values[category_name])
                if min_val <= cur_value <= max_val:
                    self.filtered_queries.update({index: values})
        return self.filtered_queries

    def filter_by_almost_equal(self, category_name, arr_of_values):
        self.filtered_queries = {}
        category_data = self.find_objects(category_name)
        for index, value in category_data.items():
            separated_value = value.split(',')
            for req_value in arr_of_values:
                if req_value in separated_value:
                    self.filtered_queries[index] = self.find_by_index(index)
        return self.filtered_queries
