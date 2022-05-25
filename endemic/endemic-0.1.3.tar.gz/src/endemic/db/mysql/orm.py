import logging
import json


class MysqlORM:

    def __init__(self, logger: logging):
        self.logging = logger
        self.__host = None
        self.__port = None
        self.__user = None
        self.__password = None
        self.__db_name = None

    def config(self, host=None, port=None, user=None, password=None, db_name=None):
        self.__host = host
        self.__port = port
        self.__user = user
        self.__password = password
        self.__db_name = db_name

    @staticmethod
    def pure_sql_request(query):
        return [query, None]

    @staticmethod
    def insert_into_table_on_duplicate_ignore(self, table, data, insert_keys):
        export_keys = list(insert_keys.keys())
        export_fields = list(insert_keys.values())

        temp = []
        values = []
        for elem in export_keys:
            if isinstance(data[elem], int):
                temp.append('%s')
                values.append(int(data[elem]))
            else:
                temp.append('%s')
                values.append(str(data[elem]))

        query = 'INSERT INTO {0} ({1}) VALUES ({2}) ON DUPLICATE KEY UPDATE id=VALUES(id)'.format(
            table,
            self.__create_list_of_keys(export_fields),
            self.__create_list_of_keys(temp)
        )

        return [query, values]

    def insert_into_table_increase_field(self, table, data, field, direction='+'):
        export_keys = list(data.keys())

        temp = []
        values = []
        for elem in export_keys:
            if isinstance(data[elem], int):
                temp.append('%s')
                values.append(int(data[elem]))
            else:
                temp.append('%s')
                values.append(str(data[elem]))

        query = 'INSERT INTO ' + str(table) + ' (' + self.__create_list_of_keys(export_keys) + ') VALUES (' \
                + self.__create_list_of_values(
            temp) + ') ON DUPLICATE KEY UPDATE ' + field + ' = ' + field + direction + '1'

        return [query, values]

    # SQL query example: SELECT * FROM {table} WHERE {field} IN ({list(data)} Order By {order} {direction} Limit {limit})
    # table - table name
    # data - dict
    # order - field name to order (string)
    # direction - ASC/DESC
    # limit - limit in format string 'start,number'
    #
    @staticmethod
    def get_row_form_table_by_field_array(table, data, field, order=None, direction='ASC', limit=None):
        format_strings = ','.join(['%s'] * len(data))
        query = 'SELECT * FROM ' + str(table) + ' WHERE ' + str(field) + ' in (%s) ' % format_strings

        if order:
            query += ' ORDER BY {} {}'.format(order, direction)

        if limit:
            query += ' LIMIT {}'.format(limit)

        return [query, tuple(data)]

    # SQL query example: SELECT * FROM {table} WHERE {field} > (value} Order By {order} {direction} Limit {limit})
    # table - table name
    # data - dict
    # order - field name to order (string)
    # direction - ASC/DESC
    # limit - limit in format string 'start,number'
    #
    @staticmethod
    def get_row_form_table_greater_then_field_array(table, value, field, order=None, direction='ASC', limit=None):
        query = 'SELECT * FROM ' + str(table) + ' WHERE ' + str(field) + ' > (%s) '

        if order:
            query += ' ORDER BY {} {}'.format(order, direction)

        if limit:
            query += ' LIMIT {}'.format(limit)

        return [query, value]

    def update_table_all_values_by_key(self, table, data, insert_keys):
        export_keys = list(insert_keys.keys())

        temp = []
        values = []
        keys = []

        for elem in export_keys:
            if elem in data:
                if isinstance(data[elem], bool):
                    temp.append('%s')
                    values.append(bool(data[elem]))
                    keys.append(str(insert_keys[elem]))
                elif isinstance(data[elem], dict):
                    temp.append('%s')
                    values.append(str(json.dumps(data[elem])))
                    keys.append(str(insert_keys[elem]))
                elif not data[elem]:
                    temp.append('%s')
                    values.append(None)
                    keys.append(str(insert_keys[elem]))
                else:
                    temp.append('%s')
                    values.append(str(data[elem]))
                    keys.append(str(insert_keys[elem]))

        if not ', '.join(['{1}=values({1})'.format(value, value) for (value) in keys]):
            return

        query = 'INSERT INTO ' + str(table) + ' (' + self.__create_list_of_values(keys) + ') VALUES (' \
                + self.__create_list_of_values(temp) + ') ON DUPLICATE KEY UPDATE ' + \
                ', '.join(['{1}=values({1})'.format(value, value) for (value) in keys])

        return [query, values]

    @staticmethod
    def delete_from_table(table, field, value):
        query = 'DELETE FROM ' + str(table) + ' WHERE ' + str(field) + ' = %s'
        return [query, value]

    @staticmethod
    def select_row_by_value_between_dates(table, field, value, date_field, date_lower, date_higher):

        query = 'SELECT * FROM ' + str(table) + ' WHERE ' + str(field) + ' in (%s) ' + \
                'AND ' + str(date_field) + ' > %s AND ' + str(date_field) + ' < %s'

        values = [value, date_lower, date_higher]

        return [query, tuple(values)]

    @staticmethod
    def __create_list_of_values(list_input):
        string_value = ','.join(str(x) for x in list_input)
        return string_value

    @property
    def user(self) -> str:
        return self.__user

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> str:
        return self.__port

    @property
    def password(self) -> str:
        return self.__password

    @property
    def db_name(self) -> str:
        return self.__db_name
