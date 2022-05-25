from functools import wraps
from typing import Any, Tuple, List, Iterator, Dict
import lmdb
import pickle as pkl


def _with_transaction(func):
    @wraps(func)
    def wrapper(slf, *args, **kwargs):
        if slf._txn is not None:
            txn = slf._txn
            return func(slf, *args, txn=txn, **kwargs)
        else:
            with slf.env.begin(write=slf.writeable, db=slf.db) as txn:
                return func(slf, *args, txn=txn, **kwargs)
    return wrapper


class LmdbDict:
    r"""
    Summary:
        Almost like standary python dict, which data stored in lmdb.
        The key/value could be any object that could be serializable with pickle.

    Usage:
        ```
        d = LmdbDict('filename', 'dbname', writeable=True)
        d[0] = 1  # set/get one value
        # multiple set/get values (using `with` clause to speed up):
        with d:
            for i in range(100):
                d[i+1] = i
        ```
    Note:
        Every key/value is a copy of database, so modify the key/value doesn't reflect to database(file).
        For example:
        ```
            d[0] = [1,2,3]  # write some data
            lst = d[0]
            lst[-1] = 4
            print(lst)      # output: [1,2,4]
            print(d[0])     # output: [1,2,3], which is different from the std dict object!
            d[0] = lst
            print(d[0])     # output: [1,2,4]
        ```
    """
    def __init__(self, file, dbname, writeable=False, **kwargs):
        self.file = file
        self.dbname = dbname
        self.env = lmdb.open(str(file), int(1e12), max_dbs=128, readonly=not writeable, **kwargs)
        self.db = self.env.open_db(dbname.encode())
        self.writeable = writeable
        self._iter = None
        self._txn = None
        self._txn4iter = None
        self._cursor = None
        self.kwargs = kwargs
    
    @_with_transaction
    def clear(self, txn):
        txn.drop(db=self.db)

    @_with_transaction
    def setdefault(self, key: Any, default: Any, txn) -> Any:
        bk = pkl.dumps(key)
        v = txn.get(bk)
        if v is not None:
            return pkl.loads(v)
        else:
            txn.put(bk, pkl.dumps(default))
            return default
        
    def update(self, dct: Dict):
        # for k in dct: self[k] = dct[k]
        with self:
            for k in dct:
                self[k] = dct[k]
    
    @_with_transaction
    def keys(self, txn) -> List[Any]:
        txn = self._txn or self.env.begin(write=False, db=self.db)
        with txn:
            return [pkl.loads(k) for k in txn.cursor().iternext(values=False)]

    @_with_transaction
    def values(self, txn) -> List[Any]:
        return [pkl.loads(v) for k, v in txn.cursor().iternext(values=True)]

    @_with_transaction
    def items(self, txn) -> List[Tuple[str, Any]]:
        txn = self._txn or self.env.begin(write=False, db=self.db)
        with txn:
            return [(pkl.loads(k), pkl.loads(v)) for k, v in txn.cursor().iternext(values=True)]

    @_with_transaction
    def __len__(self, txn) -> int:
        return len(list(txn.cursor().iternext(values=False)))

    @_with_transaction
    def __getitem__(self, k: Any, txn) -> Any:
        v = txn.get(pkl.dumps(k))
        if v:
            return pkl.loads(v)
        raise IndexError(f"There is no the key: {k}")
    
    @_with_transaction
    def __setitem__(self, k: Any, v: Any, txn) -> None:
        txn.put(pkl.dumps(k), pkl.dumps(v))
        
    @_with_transaction
    def __delitem__(self, k: Any, txn) -> None:
        txn.delete(pkl.dumps(k))
        
    def __iter__(self):
        if self._txn4iter is not None:
            self._txn4iter.abort()
            del self._txn4iter
            del self._cursor
            self._txn4iter = None
            self._cursor = None
        self._txn4iter = self.env.begin(db=self.db, write=False)
        self._cursor = self._txn4iter.cursor().iternext(values=False)
        return self
    
    def __next__(self):
        return pkl.loads(next(self._cursor))

    def __enter__(self):
        assert self._txn is None, "cannot reentrant"
        self._txn = self.env.begin(db=self.db, write=self.writeable)
        return self._txn
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self._txn.abort()
        else:
            self._txn.commit()
        self._txn = None

    def close(self):
        self.env.close()
