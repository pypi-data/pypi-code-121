#-----------------------------
# -- fundb --
# database module
#-----------------------------

import copy 
import json
import sqlite3
import multiprocessing
from typing import Any, List
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


def _from_json(data:str) -> dict:
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
    :: Document
    """

    # Private columns
    PRIVATE_COLUMNS = ["_id", "_json", "_created_at", "_modified_at"]

    def __init__(self, collection, row: sqlite3.Row):
        self.collection = collection 
        self._load(row)

    def dget(self, path:str, default=None)->Any:
        """
        Return a property by DotNotation

        ie: 
            #dget("key.deep1.deep2.deep3")

        Args:
            path:str - the dotnotation path
            default:Any - default value 
        
        Returns:
            Any
        """
        return lib.dict_get(obj=dict(self), path=path, default=default)

    def dset(self, path:str, value:Any):
        """
        Set a property by DotNotation

        Args:
            path:str - the dotnotation path
            value:Any - The value

        Returns:
            Void
        """
        data = copy.deepcopy(dict(self))
        lib.dict_set(obj=data, path=path, value=value)
        self.update(data)

    def dpop(self, path:str):
        """ 
        Remove a property by DotNotation and return the value

        Args:
            path:str

        Returns:
            Any: the value that was removed
        """
        data = copy.deepcopy(dict(self))
        v = lib.dict_pop(obj=data, path=path)
        self.update(data)
        return v

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
        data = {}
        if a and isinstance(a[0], dict):
            data.update(a[0])
        data.update(kw)

        row = self.collection.update(_id=self._id, doc=data, _as_document=False)
        self._load(row)

    def delete(self):
        """
        Delete the Doument from the collection

        Returns:
            None
        """
        self.collection.delete(self._id)
        self._empty_self()

    def commit(self):
        """
        To commit the data when it's mutated outside.
            doc = Document()
            doc["xone"][1] = True
            doc.commit()
        """
        data = dict(self)
        self.update(data)

    def _load(self, row:sqlite3.Row):
        """
        load the content into the document
        
        Args:
            row: sqlite3.Row
        """

        self._empty_self()
        row = {k: row[k] for k in row.keys()}
        _json = _from_json(row.pop("_json"))
        self._id = row.get("_id")
        doc = {
            **_json,
            **row # row columns takes precendece
        }
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
    _columns = []
    _indexes = []

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
        if not self._columns:
            with self.db:
                try:
                    _exec = self.db.execute("PRAGMA table_info(%s)" % self.name)
                    self._columns = [r["name"] for r in _exec.fetchall()]
                except: pass
        return self._columns

    @property
    def indexes(self) -> list:
        """
        Get the list of all indexes

        Returns:
            list
        """
        if not self._indexes:
            with self.db:
                try:
                    indexes = []
                    _exec = self.db.execute("PRAGMA index_list(%s)" % self.name)
                    for item in _exec.fetchall():
                        name = item["name"]
                        _i2 = self.db.execute("PRAGMA index_info(%s)" % name)
                        f = _i2.fetchone()
                        indexes.append(f["name"])
                    self._indexes = indexes
                    #return [item.keys() for item in _exec]
                except: pass
        return self._indexes

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

    # ---- methods ----

    def get(self, *a, **kw) -> Document:
        """
        Retrieve 1 document by _id, or other indexed criteria

        Args:
          _id:str - the document id
          _as_document:bool - when True return Document
          **kw other query

        Returns:
          Document

        """

        _as_document = True
        if "_as_document" in kw:
            _as_document = kw.pop("_as_document")

        filters = {}
        if a: # expecting the first arg to be _id
            filters = {"_id": a[0]}
        elif kw: # multiple 
            filters = kw
        else:
            raise Exception("Invalid Collection.get args")

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
            query += " WHERE %s " % " AND ".join(xquery)

        query += " LIMIT 1"

        xparams = list(filters.values())
        with self.db:
            _exec = self.db.execute(query, xparams)
            row = _exec.fetchone()
            if row:
                return Document(self, row) if _as_document else row
        return None

    def insert(self, doc: dict, _as_document:bool=True) -> Document:
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
            return self.get(_id=_id, _as_document=_as_document)

    def update(self, _id: str, doc: dict = {}, replace: bool = False, _as_document=True) -> Document:
        """
        To update a document

        Args:
          _id:str - document id
          doc:dict - the document to update
          replace:bool - By default document will be merged with existing data
                  When True, it will save it as is. 

        Returns:
            Document
        """
        with self.db:
            rdoc = self.get(_id=_id, _as_document=False)
            if rdoc:
                _doc = doc if replace else lib.dict_merge(_from_json(rdoc["_json"]), doc)
                ts = lib.get_timestamp()
                
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
                return self.get(_id=_id, _as_document=_as_document)
            return None

    def delete(self, _id: str) -> bool:
        """
        To delete an entry by _id
        
        Args:
            _id:str - entry id

        Returns:
            Bool
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
            query += " WHERE %s " % " AND ".join(xquery)

        # Perform JSON search, as we have JSON_FILTERS
        # Full table scan, relative to WHERE clause
        chunk = 100
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

    def add_columns(self, columns:List[str], enforce_index=False):
        """
        To add columns. With options to add indexes

        Args:
            columns: 
                List[str] -> "COLUMN:TYPE@INDEX"
                    [
                        "column", # column only. Type is in
                        "column:type", # column and type
                        "column:type@index", # column, type and index
                        "column:type@unique" # column type and unique index
                        "column@unique" # column and unique index. Type is inferred
                    ]
            
            enforce_index:
                bool - To make all prop an index.
        Returns:
            None
        """
        cols_stmt = []
        for idx in columns:
            if isinstance(idx, str):
                _type = "TEXT"
                indx = False
                col = idx
                if "@" in col:
                    col, indx =  col.split("@")
                    indx = "UNIQUE" if indx.upper() == "UNIQUE" else True
                if ":" in col:
                    col, _type = col.split(":")
                if enforce_index and indx != "UNIQUE":
                    indx = True
                cols_stmt.append((col, _type or "TEXT", indx))


        with self.db:
            for _ in cols_stmt:
                try:
 
                    col, coltype, colindex = _

                    # Add column if not exists
                    if col not in self.columns: 
                        self.db.execute("ALTER TABLE %s ADD COLUMN %s %s DEFAULT NULL" % (self.name, col, coltype))

                    # Add index if not exists
                    if colindex and col not in self.indexes:
                        index_stmt = None
                        # unique
                        if isinstance(colindex, str) and colindex.upper() == "UNIQUE":
                            index_stmt = "UNIQUE"
                        # regular
                        elif colindex is True:
                            index_stmt = ""
                        if index_stmt is not None:
                            self.db.execute("CREATE %s INDEX %s ON %s (%s)" % (index_stmt, col+"__idx", self.name, col))
                except Exception as e: pass
        # reset columns
        self._columns = []
        self._indexes = []

    def add_indexes(self, columns:List[str]):
        """
        To indexed columns

        Args: 
            columns:
                List[str]. Documentation-> #add_columns
        """
        self.add_columns(columns=columns, enforce_index=True)


    def __len__(self):
        return self.size
