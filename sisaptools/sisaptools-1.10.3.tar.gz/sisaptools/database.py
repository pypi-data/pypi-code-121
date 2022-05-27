# -*- coding: utf8 -*-

"""
Eines per a la connexió a bases de dades relacionals (Oracle i MariaDB)
i la manipulació de les seves dades i estructures.
"""

import datetime
import os
import random
import time

import cx_Oracle
import MySQLdb.cursors

from .constants import (IS_PYTHON_3, TMP_FOLDER,
                        MARIA_CHARSET, MARIA_COLLATE, MARIA_STORAGE)
from .aes import AESCipher
from .services import DB_INSTANCES, DB_CREDENTIALS
from .textfile import TextFile


class Database(object):
    """
    Classe principal. S'instancia per cada connexió a una base de dades.
    Tots els mètodes es poden utilitzar per Oracle i MariaDB
    si no s'especifica el contrari.
    """

    def __init__(self, instance, schema, retry=None):
        """
        Inicialització de paràmetres i connexió a la base de dades.
        En cas d'error, intenta cada (retry) segons.
        """
        hacked_instance = instance + 'p' if schema == 'prod' else instance
        attributes = DB_INSTANCES[hacked_instance]
        self.engine = attributes['engine']
        self.host = attributes.get('host')
        self.port = attributes.get('port')
        if self.engine == 'my':
            self.local_infile = attributes['local_infile']
            self.user, self.password = DB_CREDENTIALS[instance]
            self.database = schema
        elif self.engine == 'ora':
            self.sid = attributes.get('sid')
            self.service_name = attributes.get('service_name')
            self.string = attributes.get('string')
            self.user, self.password = DB_CREDENTIALS[instance][schema]
        self.available = False
        while not self.available:
            try:
                self.connect()
            except Exception as e:
                if any([word in str(e)
                        for word in ('1049', 'Unknown database')]):
                    self.connect(existent=False)
                    self.recreate_database()
                elif retry:
                    time.sleep(retry)
                else:
                    raise
            else:
                self.available = True

    def connect(self, existent=True):
        """Desencripta password i connecta a la base de dades."""
        password = AESCipher().decrypt(self.password) if self.password else ''
        if self.engine == 'my':
            self.connection = MySQLdb.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=password,
                db=self.database if existent else 'information_schema',
                cursorclass=MySQLdb.cursors.SSCursor,
                charset=MARIA_CHARSET,
                use_unicode=IS_PYTHON_3,
                local_infile=1 * self.local_infile
            )
        elif self.engine == 'ora':
            if self.sid:
                self.dsn = cx_Oracle.makedsn(self.host, self.port, self.sid)
            elif self.service_name:
                self.dsn = cx_Oracle.makedsn(self.host,
                                             self.port,
                                             service_name=self.service_name)
            else:
                self.dsn = self.string
            self.connection = cx_Oracle.connect(self.user, password, self.dsn)

    def execute(self, sql):
        """Executa una sentència SQL."""
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        self.cursor.close()
        self.connection.commit()

    def recreate_database(self):
        """Elimina i torna a crear una base de dades (MariaDB)."""
        self.execute('drop database if exists {}'.format(self.database))
        sql = 'create database {} character set {} collate {}'
        self.execute(sql.format(self.database, MARIA_CHARSET, MARIA_COLLATE))
        self.execute('use {}'.format(self.database))

    def create_table(self, table, columns,
                     pk=None,
                     partition_type='hash', partition_id='id', partitions=None,
                     storage=MARIA_STORAGE, remove=False):
        """Crea una taula a la base de dades."""
        if remove:
            self.drop_table(table)
        if pk:
            if self.engine == 'my':
                spec = '({}, PRIMARY KEY ({}))'.format(', '.join(columns),
                                                       ', '.join(pk))
            elif self.engine == 'ora':
                spec = '({}, CONSTRAINT {}_pk PRIMARY KEY ({}))'.format(
                    ', '.join(columns),
                    table,
                    ', '.join(pk))
        else:
            spec = '({})'.format(', '.join(columns))
        if self.engine == 'my':
            this = ' engine {} character set {} collate {}'
            spec += this.format(storage, MARIA_CHARSET, MARIA_COLLATE)
        if partitions:
            this = ' partition by {} ({}) {}'
            spec += this.format(partition_type, partition_id,
                                'partitions {}'.format(partitions)
                                if partition_type == 'hash'
                                else '({})'.format(', '.join(partitions)))
        try:
            self.execute('create table {} {}'.format(table, spec))
        except Exception as e:
            s = str(e)
            if not any([word in s for word in ('1050', 'ORA-00955')]):
                raise e

    def drop_table(self, table):
        """Elimina una taula."""
        if self.engine == 'my':
            self.execute('drop table if exists {}'.format(table))
        elif self.engine == 'ora':
            try:
                self.execute('drop table {} PURGE'.format(table))
            except Exception:
                pass

    def rename_table(self, old_name, new_name, ts=False):
        """Reanomena una taula."""
        if ts:
            ara = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            new_name += '_{}'.format(ara)
        self.drop_table(new_name)
        try:
            if self.engine == 'my':
                self.execute('rename table {} to {}'.format(old_name,
                                                            new_name))
            elif self.engine == 'ora':
                self.execute('rename {} to {}'.format(old_name, new_name))
        except Exception:
            done = False
        else:
            done = True
        return done

    def get_all(self, sql, limit=None):
        """
        Crea un generator que retorna d'un en un tots els registres
        obtinguts per una sentència SQL.
        """
        if limit:
            sql = self.get_limit_clause(sql, limit)
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        for row in self.cursor:
            yield row
        self.cursor.close()

    def get_many(self, sql, n, limit=None):
        """
        Crea un generator que retorna de n en n tots els registres
        obtinguts per una sentència SQL.
        """
        if limit:
            sql = self.get_limit_clause(sql, limit)
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        while True:
            result = self.cursor.fetchmany(n)
            if not result:
                break
            yield result
        self.cursor.close()

    def get_limit_clause(self, sql, rows):
        """
        Modifica la sentència SQL de get_all o get_many
        per limitar el número de registres.
        """
        if self.engine == 'my':
            spec = ' limit {}'.format(rows)
        elif self.engine == 'ora':
            particula = 'and' if 'where' in sql else 'where'
            spec = ' {} rownum <= {}'.format(particula, rows)
        sql += spec
        return sql

    def get_one(self, sql):
        """Retorna un registre d'una sentència SQL."""
        self.cursor = self.connection.cursor()
        self.cursor.execute(sql)
        resul = self.cursor.fetchone()
        self.cursor.close()
        return resul

    def list_to_table(self, iterable, table, partition=None, chunk=None):
        """
        Insereix un iterable a una taula:
          -a MariaDB utilitza txt_to_table
          -a Oracle utilitza _list_to_table_oracle
        """
        if self.engine == 'my':
            rand = random.randrange(0, 2 ** 64)
            filename = '{}/{}_{}.txt'.format(TMP_FOLDER, table, rand)
            delimiter = '@,'
            endline = '|;'
            with TextFile(filename) as file:
                file.write_iterable(iterable, delimiter, endline)
            self.file_to_table(filename, table, partition, delimiter, endline)
        elif self.engine == 'ora':
            values = [':{}'.format(i + 1) for i in range(len(iterable[0]))]
            values = ', '.join(values)
            sql = 'insert into {} VALUES ({})'.format(table, values)
            if chunk:
                for data in (iterable[i:i + chunk]
                             for i in range(0, len(iterable), chunk)):
                    self._list_to_table_oracle(sql, data)
            else:
                self._list_to_table_oracle(sql, iterable)

    def _list_to_table_oracle(self, sql, iterable):
        """Auxiliar per càrrega a oracle."""
        self.cursor = self.connection.cursor()
        self.cursor.prepare(sql)
        self.cursor.executemany(None, iterable)
        self.cursor.close()
        self.connection.commit()

    def file_to_table(self, filename, table, partition, delimiter, endline):
        """Carrega un fitxer a una taula (MariaDB)."""
        sql = "LOAD DATA {local} INFILE '{filename}' \
               ignore INTO TABLE {table} {partition} \
               CHARACTER SET {charset} \
               FIELDS TERMINATED BY '{delimiter}' \
               LINES TERMINATED BY '{endline}'"
        sql = sql.format(
            local='LOCAL' if self.local_infile else '',
            filename=filename,
            table=table,
            partition='PARTITION ({})'.format(partition) if partition else '',
            charset=MARIA_CHARSET,
            delimiter=delimiter,
            endline=endline
        )
        self.execute(sql)
        os.remove(filename)

    def get_tables(self):
        """Retorna les taules de la base de dades."""
        if self.engine == 'my':
            sql = "select table_name, table_rows \
                   from information_schema.tables \
                   where table_schema = '{}'".format(self.database)
        elif self.engine == 'ora':
            sql = "select table_name, num_rows from all_tables"
        tables = {table: rows for table, rows in self.get_all(sql)}
        return tables

    def get_table_owner(self, table, dblink=None):
        """Retorna el propietari i el nom original d'una taula (Oracle)."""
        table = table.upper()
        dblink_txt = "@{}".format(dblink.upper()) if dblink else ""
        try:
            sql = "select table_name from user_tables{} \
                   where table_name = '{}'"
            table, = self.get_one(sql.format(dblink_txt, table))
            owner, = self.get_one('select user from dual')
        except TypeError:
            try:
                sql = "select table_owner, table_name from user_synonyms{} \
                       where synonym_name = '{}'"
                owner, table = self.get_one(sql.format(dblink_txt, table))
                try:
                    sql = "select table_owner, table_name from all_synonyms{} \
                           where owner = '{}' and synonym_name = '{}'"
                    owner, table = self.get_one(sql.format(dblink_txt, owner,
                                                           table))
                except TypeError:
                    pass
            except TypeError:
                try:
                    sql = "select table_owner, table_name from all_synonyms{} \
                           where owner = 'PUBLIC' and \
                                 synonym_name = '{}' and \
                                 db_link is null"
                    owner, table = self.get_one(sql.format(dblink_txt, table))
                except TypeError:
                    sql = "select owner, table_name from all_tables{} \
                           where table_name = '{}'"
                    owner, table = self.get_one(sql.format(dblink_txt, table))
        return owner, table

    def get_table_count(self, table, owner=None, dblink=None):
        """Retorna el número de registres d'una taula."""
        if self.engine == 'my':
            sql = "select table_rows from information_schema.tables \
                   where table_schema = '{}' and table_name = '{}'"
            sql = sql.format(self.database, table)
        elif self.engine == 'ora':
            if not owner:
                owner, table = self.get_table_owner(table, dblink=dblink)
            dblink_txt = "@{}".format(dblink.upper()) if dblink else ""
            sql = "select nvl(num_rows, 0) from all_tables{} \
                   where owner = '{}' and table_name = '{}'"
            sql = sql.format(dblink_txt, owner.upper(), table.upper())
        rows, = self.get_one(sql)
        return rows

    def get_table_partitions(self, table, owner=None, dblink=None):
        """
        Retorna un diccionari amb les particions d'una taula
        i el seu número de registres.
        """
        if self.engine == 'my':
            sql = "select engine from information_schema.tables \
                   where table_schema = '{}' and table_name = '{}'"
            sql = sql.format(self.database, table)
            is_merge = 'MRG' in self.get_one(sql)[0]
            if is_merge:
                sql = 'show create table {}'.format(table)
                create = self.get_one(sql)[1]
                raw_tables = create.split('UNION=(')[1][:-1].split(',')
                tables = [tab.replace('`', '') for tab in raw_tables]
                sql = "select table_name, table_rows \
                       from information_schema.tables \
                       where table_schema = '{}' and table_name in {}"
                sql = sql.format(self.database, tuple(tables))
            else:
                sql = "select partition_name, table_rows \
                       from information_schema.partitions \
                       where table_schema = '{}' and table_name = '{}' \
                       and partition_name is not null"
                sql = sql.format(self.database, table)
        elif self.engine == 'ora':
            if not owner:
                owner, table = self.get_table_owner(table, dblink=dblink)
            dblink_txt = "@{}".format(dblink.upper()) if dblink else ""
            sql = "select partition_name, nvl(num_rows, 0) \
                   from all_tab_partitions{} \
                   where table_owner = '{}' and table_name = '{}'"
            sql = sql.format(dblink_txt, owner.upper(), table.upper())
        partitions = {}
        for partition, rows in self.get_all(sql):
            partitions[partition] = rows
        return partitions

    def get_table_columns(self, table, owner=None, dblink=None):
        """Retorna una llista amb les columnes de la taula."""
        if self.engine == 'my':
            sql = "select column_name from information_schema.columns \
                   where table_schema = '{}' and table_name = '{}' \
                   order by ordinal_position".format(self.database, table)
        elif self.engine == 'ora':
            if not owner:
                owner, table = self.get_table_owner(table, dblink=dblink)
            dblink_txt = "@{}".format(dblink.upper()) if dblink else ""
            sql = "select column_name from all_tab_columns{} \
                   where owner = '{}' and table_name='{}' \
                   order by column_id".format(dblink_txt, owner.upper(),
                                              table.upper())
        columns = [column for column, in self.get_all(sql)]
        return columns

    def get_column_information(self, column, table, owner=None,
                               desti='my', dblink=None):
        """
        Retorna un diccionari amb les instrucciones necessàries
        tant per crear com per consultar la columna especificada.
        """
        if self.engine == 'my':
            sql = "select column_type, data_type, character_maximum_length, \
                   numeric_precision from information_schema.columns \
                   where table_schema = '{}' and table_name = '{}' \
                   and column_name = '{}'".format(self.database, table, column)
            done, type, char, num = self.get_one(sql)
            length, precision, scale = None, None, None
        elif self.engine == 'ora':
            if not owner:
                owner, table = self.get_table_owner(table, dblink=dblink)
            dblink_txt = "@{}".format(dblink.upper()) if dblink else ""
            sql = "select data_type, data_length, data_precision, data_scale \
                   from all_tab_columns{} \
                   where owner = '{}' and table_name = '{}' \
                   and column_name = '{}'".format(dblink_txt, owner.upper(),
                                                  table.upper(),
                                                  column.upper())
            type, length, precision, scale = self.get_one(sql)
            done, char, num = None, None, None
            words_in = ('DAT', 'VAL_D_V')
            words_out = ('EDAT', 'RE_DATA_VIGEN', 'DATAANY')
            if type == 'NUMBER' and \
               any([word in column.upper() for word in words_in]) and \
               not any([word in column.upper() for word in words_out]):
                type = 'DATE_J'
            if column.upper() == "VISI_DATA_UPDA":
                type = "DATETIME"
        param = {'column': column, 'length': length,
                 'precision': precision, 'scale': scale,
                 'done': done, 'char': char, 'num': num}
        conv = {('my', 'date', 'my', 'create'): '{column} {done}',
                ('my', 'date', 'my', 'query'):
                    "date_format({column}, '%Y%m%d')",
                ('my', 'date', 'ora', 'create'): '{column} date',
                ('my', 'date', 'ora', 'query'): column,
                ('my', 'int', 'my', 'create'): '{column} {done}',
                ('my', 'int', 'my', 'query'): column,
                ('my', 'int', 'ora', 'create'): '{column} number({num})',
                ('my', 'int', 'ora', 'query'): column,
                ('my', 'bigint', 'my', 'create'): '{column} {done}',
                ('my', 'bigint', 'my', 'query'): column,
                ('my', 'bigint', 'ora', 'create'): '{column} number({num})',
                ('my', 'bigint', 'ora', 'query'): column,
                ('my', 'double', 'my', 'create'): '{column} {done}',
                ('my', 'double', 'my', 'query'): column,
                ('my', 'double', 'ora', 'create'): '{column} number({num})',
                ('my', 'double', 'ora', 'query'): column,
                ('my', 'varchar', 'my', 'create'): '{column} {done}',
                ('my', 'varchar', 'my', 'query'): column,
                ('my', 'varchar', 'ora', 'create'):
                    '{column} varchar2({char})',
                ('my', 'varchar', 'ora', 'query'): column,
                ('ora', 'DATE', 'my', 'create'): '{column} date',
                ('ora', 'DATE', 'my', 'query'):
                    "to_char({column}, 'YYYYMMDD')",
                ('ora', 'DATE', 'ora', 'create'): '{column} date',
                ('ora', 'DATE', 'ora', 'query'): column,
                ('ora', 'DATE_J', 'my', 'create'): '{column} date',
                ('ora', 'DATE_J', 'my', 'query'):
                    "case when {column} > 3000000 then null else to_char(to_date({column}, 'J'), 'YYYYMMDD') end",  # noqa
                ('ora', 'DATE_J', 'ora', 'create'): '{column} date',
                ('ora', 'DATE_J', 'ora', 'query'):
                    "case when {column} > 3000000 then null else to_date({column}, 'J') end",  # noqa
                ('ora', 'DATETIME', 'my', 'create'): '{column} datetime',
                ('ora', 'DATETIME', 'my', 'query'):
                    "to_char({column}, 'YYYY-MM-DD HH24:MI:SS')",
                ('ora', 'DATETIME', 'ora', 'create'): '{column} date',
                ('ora', 'DATETIME', 'ora', 'query'): column,
                ('ora', 'TIMESTAMP(6)', 'my', 'create'): '{column} datetime',
                ('ora', 'TIMESTAMP(6)', 'my', 'query'):
                    "to_char({column}, 'YYYY-MM-DD HH24:MI:SS')",
                ('ora', 'TIMESTAMP(6)', 'ora', 'create'): '{column} date',
                ('ora', 'TIMESTAMP(6)', 'ora', 'query'): column,
                ('ora', 'NUMBER', 'my', 'create'):
                    '{column} decimal(6,3)' if column.upper() == "GMA_IND_CMPLX"  # noqa
                    else '{column} double' if scale
                    else '{column} int' if not precision or precision < 10
                    else '{column} bigint',
                ('ora', 'NUMBER', 'my', 'query'): column,
                ('ora', 'NUMBER', 'ora', 'create'):
                    '{column} number({precision}, {scale})' if scale
                    else '{column} number',
                ('ora', 'NUMBER', 'ora', 'query'): column,
                ('ora', 'VARCHAR2', 'my', 'create'):
                    "{column} varchar({length})",
                ('ora', 'VARCHAR2', 'my', 'query'):
                    'ltrim(rtrim({column}))' if length and length > 49 else column,  # noqa
                ('ora', 'VARCHAR2', 'ora', 'create'):
                    '{column} varchar2({length})',
                ('ora', 'VARCHAR2', 'ora', 'query'): column,
                ('ora', 'CHAR', 'my', 'create'):
                    "{column} varchar({length})",
                ('ora', 'CHAR', 'my', 'query'):
                    'ltrim(rtrim({column}))' if length and length > 49 else column,  # noqa
                ('ora', 'CHAR', 'ora', 'create'):
                    '{column} char({length})',
                ('ora', 'CHAR', 'ora', 'query'): column,
                ('ora', 'NVARCHAR2', 'my', 'create'):
                    "{column} varchar({length})",
                ('ora', 'NVARCHAR2', 'my', 'query'):
                    'ltrim(rtrim({column}))' if length and length > 49 else column,  # noqa
                ('ora', 'NVARCHAR2', 'ora', 'create'):
                    '{column} nvarchar2({length})',
                ('ora', 'NVARCHAR2', 'ora', 'query'): column,
                ('ora', 'NCLOB', 'ora', 'create'): '{column} nclob',
                ('ora', 'NCLOB', 'ora', 'query'): column}
        resul = {key: conv[(self.engine, type, desti, key)].format(**param)
                 for key in ('create', 'query')}
        return resul

    def set_statistics(self, table):
        """Calcula les estadístiques d'una taula d'Oracle."""
        self.cursor = self.connection.cursor()
        proc = 'DBMS_STATS.GATHER_TABLE_STATS'
        self.cursor.callproc(proc, (self.user, table.upper()))
        self.cursor.close()
        self.connection.commit()

    def set_grants(self, grants, tables, users, inheritance=True):
        """Estableix grants."""
        comparacio = str if IS_PYTHON_3 else basestring
        if isinstance(grants, comparacio):
            grants = (grants,)
        if isinstance(tables, comparacio):
            tables = (tables,)
        if isinstance(users, comparacio):
            users = (users,)
        sql = 'grant {} on {} to {} {}'
        self.execute(sql.format(', '.join(grants),
                                ', '.join(tables),
                                ', '.join(users),
                                'with grant option' if inheritance else ''))

    def disconnect(self):
        """Desconnecta de la base de dades."""
        self.connection.close()

    def __enter__(self):
        """Context manager."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager."""
        self.disconnect()
