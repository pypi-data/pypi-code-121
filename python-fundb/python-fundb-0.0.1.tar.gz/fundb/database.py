#-----------------------------
# -- fundb --
# database module
#-----------------------------

import json
import sqlite3
import multiprocessing
from typing import Any
from ctypes import Union
from . import lib, cursor, search

def _to_json(data:dict) -> str:
    """
    Convert data to json string

    Args:
        data: dict

    Returns:
        str

    """
    return json.dumps(data)


def _from_json(data) -> dict:
    """
    Convert data to json string

    Args:
        data: str

    Returns:
        dict
        
    """
    return json.loads(data)


def _row_to_dict(row:sqlite3.Row) -> dict:
    """
    Properly parse the SQLite#Row to document dict 

    Args:
        row: sqlite.Row

    Returns
        dict
    """
    _json = row["_json"]
    doc = {**_from_json(_json)}
    doc.update({k: row[k] for k in row.keys() if k not in ["_json"]})
    return doc


def _parse_smart_filtering(filters: dict, indexed_columns:list=[]) -> dict:
    """
    Smart Filter
    Breaks down the filters based on type. 
    - SQL_FILTERS: is more restrictive on what can be queried. 
                  Will be done at the SQL level
    - JSON_FILTERS: is more loose. 
                    It contains items that are not in the sql_filters. 
                    Will be done at the JSON level
    
    Args:
      filters: dict  - 
      indexed_columns: list - List of indexed sql columns/or other columns in the table 
                       this will allow with the smart filtering
      
    Returns: 
      dict:
        SQL_FILTERS
        JSON_FILTERS
    """

    # filter SQL_OPERATORS filters
    sql_filters = []
    json_filters = {}
    for k, v in filters.items():
        if search.FILTER_OPERATOR in k:
            f, op = k.split(search.FILTER_OPERATOR)
            if f in indexed_columns and op in search.SQL_OPERATORS:
                sql_filters.append((f, search.SQL_OPERATORS[op], v))
                continue
        else:
            if k in indexed_columns:
                sql_filters.append((k, search.SQL_OPERATORS["eq"], v))
                continue
        json_filters[k] = v
              
    return {
        "SQL_FILTERS": sql_filters,
        "JSON_FILTERS": json_filters
    }


class Database(object):
    """
    ::Database
    """

    def __init__(self, filename=":memory:", search_proc=4):
        """
        Connect database 

        Return:
        """
        self.conn = sqlite3.connect(filename, isolation_level=None)
        self.conn.execute('pragma journal_mode=wal')
        self.conn.row_factory = sqlite3.Row
        self._search_proc = search_proc

    def select(self, name):
        """
        Select a collection

        Returns:
            Collection
        """
        return Collection(self, name)

    def __getattr__(self, __name: str):
        """
        To magically select a collection
        ie:
            db = Database()
            coll = db.collection_name
            ->  assert coll.name == 'collection_name'

        Returns:
            Collection
        """
        return self.select(__name)

    @property
    def collections(self) -> list:
        """
        List collections

        Returns: 
          List
        """
        with self.conn:
            q = "SELECT name FROM sqlite_master WHERE type=?"
            _exec = self.conn.execute(q, ('table', ))
            return [item["name"] for item in _exec.fetchall()]

    def sync(self):
        pass

class Document(dict):
    """
    ::Document
    """

    def __init__(self, collection, row: sqlite3.Row):
        self.collection = collection 
        self._load(row)
        
    def __getattr__(self, name):
        return self[name]

    def update(self, *a, **kw):
        """
        Update the active Document
        ie:
            #update(key=value, key2=value2, ...)
            #update({ "key": value, "key2": value2 })
        
        Args:
            *args
            **kwargs

        Returns:
            Document
        """
        _ = {}
        if a and isinstance(a[0], dict):
            _.update(a[0])
        _.update(kw)
        self._load(self.collection.update(_id=self._id, doc=_, as_document=False))

    def delete(self):
        """
        Delete the Doument

        Returns:
            None
        """
        self.collection.delete(self._id)
        self._empty_self()

    def _load(self, row:sqlite3.Row):
        """
        load the content into the document
        
        Args:
            row: sqlite3.Row
        """
        self._empty_self()
        self._id = row["_id"]
        doc = {}
        if "_json" in row:
            doc = {**_from_json(row["_json"])}
        doc.update({k: row[k] for k in row.keys()})
        super().__init__(doc)

    def _empty_self(self):
        """ clearout all properties """
        for _ in list(self.keys()):
            if _ in self:
                del self[_]

class Collection(object):
    """
    ::Collection
    """
    # Column you can't query
    NON_QUERYABLE_COLUMNS = ["_json"]
    DEFAULT_COLUMNS = ["_id", "_json", "_created_at", "_modified_at"]

    def __init__(self, db, name):
        self.name = name
        self.db = db.conn
        self.conn = db.conn
        self._create()

    def _create(self):
        """
        Create a table/collection

        Returns:
          None
        """
        with self.db:
            q = "CREATE TABLE IF NOT EXISTS %s (_id VARCHAR(32) PRIMARY KEY, _json TEXT, _created_at TIMESTAMP, _modified_at TIMESTAMP)" % self.name
            self.db.execute(q)

    # ---- properties ----

    @property
    def columns(self) -> list:
        """ 
        Get the list of all the columns name

        Returns:
            list
        """
        with self.db:
            try:
                _exec = self.db.execute("SELECT * FROM %s LIMIT 1" % self.name)
                return _exec.fetchall()[0].keys()
            except: pass
        return []

    @property
    def indexes(self) -> list:
        """
        Get the list of all indexes

        Returns:
            list
        """
        with self.db:
            try:
                _exec = self.db.execute("SELECT * FROM %s WHERE type=?" % "sqlite_master", ("index",))
                return [item["tbl_name"] for item in _exec]
            except: pass
        return []

    @property
    def size(self) -> int:
        """
        Get the total entries in the collection

        Returns:
            int
        """
        with self.db:
            _exec = self.db.execute("SELECT count(*) FROM %s;" % self.name)
            return _exec.fetchone()[0]
        return 0

    # ---- methods ----

    def get(self, _id: str, as_document: bool = True) -> Document:
        """
        Retrieve a document by _id

        Args:
          _id:str - the document id
          as_document:bool - when True it will return the raw format of the data

        Returns:
          Document

        """
        with self.db:
            q = "SELECT * from %s WHERE _id=? LIMIT 1" % self.name
            _exec = self.db.execute(q, (_id,))
            row = _exec.fetchone()
            if row:
                return Document(self, row) if as_document else row
            return None

    def insert(self, doc: dict, as_document:bool=True) -> Document:
        """
        Insert a new document in collection

        use Smart Insert, by checking if a value in the doc in is a column.
        
        Args:
          doc:dict - Data to be inserted

        Returns:
            Document
        """
        if not isinstance(doc, dict):
            raise TypeError('Invalid data type. Must be a dict')

        with self.db:
            _id = lib.gen_id()
            ts = lib.get_timestamp()
            xcolumns = self.DEFAULT_COLUMNS[:]
            xparams = [_id, _to_json(doc), ts, ts]
            q = "INSERT INTO %s " % self.name
            
            # indexed data
            # some data can't be overriden 
            for col in self.columns:
                if col in doc and col not in xcolumns:
                    _data = doc[col]
                    if _data:
                        xcolumns.append(col)
                        xparams.append(_data)

            q += " ( %s ) VALUES ( %s ) " % (",".join(xcolumns), ",".join(["?" for _ in xparams]))
            
            self.db.execute(q, xparams)
            return self.get(_id, as_document=as_document)

    def update(self, _id: str, doc: dict = {}, replace: bool = False, as_document=True) -> Document:
        """
        To update a document

        Args:
          _id:str - document id
          doc:dict - the document to update
          replace:bool - to completely replace the document

        Returns:
            Document
        """
        with self.db:
            rdoc = self.get(_id, as_document=False)
            if rdoc:
                _doc = doc if replace else lib.dict_merge(_from_json(rdoc["_json"]), doc)
                ts = lib.get_timestamp()
                q = "UPDATE %s SET _json=?, _modified_at=? WHERE _id=?" % self.name
                
                if "_id" in _doc:
                    del doc["_id"]

                xcolumns = ["_json", "_modified_at"]
                xparams = [_to_json(_doc), ts]

                q = "UPDATE %s SET " % self.name
                
                # indexed data
                # some data can't be overriden 
                for col in self.columns:
                    if col in _doc and col not in xcolumns:
                        _data = _doc[col]
                        if _data:
                            xcolumns.append(col)
                            xparams.append(_data)
                q += ",".join(["%s = ?" % _ for _ in xcolumns])
                q += " WHERE _id=?"
                xparams.append(_id)
                _exec = self.db.execute(q, xparams)
                return self.get(_id, as_document=as_document)
            return None

    def replace(self, _id:str, doc:dict, as_document=True) -> Document:
        """
        To replace a document with a new document
        """
        return self.update(_id=_id, doc=doc, replace=True, as_document=as_document)

    def unset(self, _id: str, attrs: list = []):
        """
        To remove atrributes
        """

    def delete(self, _id: str) -> bool:
        """
        To delete an entry by _id
        """
        with self.db:
            self.db.execute("DELETE FROM %s WHERE _id=?" % (self.name), (_id, ))
        return True

    def find(self, filters: dict = {}, sort: list = [], limit: int = 10, skip: int = 0) -> cursor.Cursor:
        """
        To query a collection
        Smart Query
          Allow to use primary indexes from sqlite 
          then do the xtra from parsing the documents
          
        Args:
          filters:dict - 
          sort:list - [(column, order[-1|1])]
          limit:int - 
          skit:int - 

        Returns:
          cursor.Cursor
        """

        # SMART QUERY
        # Do the primary search in the columns
        # If there is more search properties, take it to the json
        xparams = []
        xquery = []
        smart_filters = _parse_smart_filtering(filters, indexed_columns=self.columns)
        
        # Build the SQL query
        query = "SELECT * FROM %s " % self.name

        # Indexed filtering
        if smart_filters["SQL_FILTERS"]:
            for f in smart_filters["SQL_FILTERS"]:
                xquery.append(" %s %s" % (f[0], f[1]))
                if isinstance(f[2], list):
                    for _ in f[2]:
                        xparams.append(_)
                else:
                    xparams.append(f[2])
        if xquery and xparams:
            query += " WHERE %s " % ",".join(xquery)

        # Perform JSON search, as we have JSON_FILTERS
        # Full table scan, relative to WHERE clause
        chunk = 2
        if smart_filters["JSON_FILTERS"]:
            _exec = self.db.execute(query, xparams)
            data = []
            while True:
                chunked = _exec.fetchmany(chunk)
                if chunked:
                    rows = [_row_to_dict(row) for row in chunked]
                    for r in search.execute(rows, smart_filters["JSON_FILTERS"]):
                        data.append(r)
                else:
                    break
            if data:
                data = [Document(self, l1) for l1 in data]
            return cursor.Cursor(data, sort=sort, limit=limit, skip=skip)

        # Skip JSON SEARCH, use only SQL.
        # No need to look into the JSON. The DB is enough
        else:
            # order by
            if sort:
                query += " ORDER BY "
                for _ in sort:
                    query += " %s %s" % (_[0], "DESC" if _[0] == -1 else "ASC")
           
            # limit/skip
            if limit or skip:
                query += " LIMIT ?, ?"
                xparams.append(skip or 0)
                xparams.append(limit or 10)

            _exec = self.db.execute(query, xparams)            
            data = [Document(self, _row_to_dict(row)) for row in _exec.fetchall()]
            return cursor.Cursor(data)

    def drop(self):
        """
        Drop/Delete a table/collection

        Returns:
            None

        """
        with self.db:
            self.db.execute("DROP TABLE %s " % self.name)

    def ensure_columns(self, columns:list):
        """
        To add columns 

        Args:
            colums: list
                [
                    (column, type),
                    (column, type)
                ]

        Returns:
            None
        """
        with self.db:
            _columns = self.columns
            for _ in columns:
                col, coltype = _

                if col in _columns: # column exist already
                    continue

                try:
                    # attempt to add column
                    q = "ALTER TABLE %s ADD COLUMN %s %s DEFAULT NULL" % (self.name, col, coltype)
                    self.db.execute(q)
                except:
                    pass

    def ensure_indexes(self, indexes:list):
        """
        To add indexes

        Args:
            indexes: list
                [
                    (column, type),
                    (column, type)
                ]

        Returns:
            None
        """
        with self.db:
            columns = self.columns
            _indexes = self.indexes
            
            for _ in indexes:
                col, coltype = _

                if col in columns: # column exist already
                    continue
                try:
                    # attempt to add column
                    if col not in columns:
                        q = "ALTER TABLE %s ADD COLUMN %s %s DEFAULT NULL" % (self.name, col, coltype)
                        self.db.execute(q)
                    
                    # attempt to add index
                    if col not in _indexes: 
                        self.db.execute("CREATE INDEX %s ON %s (%s)" % (col+"_index", self.name, col))
                except:
                    pass

    def __len__(self):
        return self.size
