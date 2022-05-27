'''
项目介绍
    layDB 是一款非关系型数据库, 具有以下特点：
        ● 免安装, 开箱即用。(只需使用pip安装Python库)
        ● 无须启动/停止, 不操作时不占用CPU和内存。
        ● 无须建表和字段。
        ● 可以存储任何"无须保持活跃"的Python对象, 如:int、str、set、function、type、pandas的对象、tensorflow的对象、
          opencv的对象等。(requests等需要保持网络连接的对象无法存储)
        ● 数据文件占用容量少, 且每个项目可单独指定数据路径, 方便使用Git等工具进行备份。
        ● 语法简洁清晰, 极易上手。

已实现的功能
    ● 增、删、改、查
    ● 并集、交集、补集、差集（先进行集合运算，再对符合条件的条目进行增/删/改/查）
    ● 切片、索引（可在增、删、改、查中切片和索引，使只操作指定条目）
    ● 排序（按排序后的顺序进行增/删/改/查）
    ● 存在时更新，不存在时新增
    ● 限定只查询部分字段
'''

from math import ceil, floor
from re import search as ReSearch
from copy import deepcopy
from collections import deque
from pathlib import Path as libpath
from pickle import loads as pickle_loads
from pickle import dumps as pickle_dumps
from .localtool import write_pickle
from .pk_factory import pk_factory
from .toolkit.data_structures import SetAttrError
from .toolkit.data_structures import undefined
from .toolkit.sorted_parts import sorted_parts as SorPa
from .cbc256 import cbc256, random_bytes


_newpk = pk_factory().pk1
_WindowsPath = type(libpath(''))
_ObjSet = object.__setattr__
def uniset(line): return True
def empset(line): return False


class _Factory:
    ''' 不可变类型, 创建后不允许修改. '''
    def __init__(self, filtor=uniset):
        if filtor is not empset:
            filtor = filtor or uniset
        object.__setattr__(self, 'filtor', filtor)

    def __setattr__(self, key, value): raise SetAttrError('_Factory是不可变对象')
    def __bool__(self): return True  # 下面有一个 factory or _Factory(uniset)

    def __and__(self, factory):  # 交集
        a = factory.filtor
        b = self.filtor
        if a is uniset: return _Factory(b)
        if b is uniset: return _Factory(a)
        if a and b:  # a和b有可能是empset
            return _Factory(lambda line: a(line) and b(line))  # factory.放在self.前面可以节省一点性能
        return _Factory(empset)

    def __or__(self, factory):  # 并集
        a = factory.filtor
        b = self.filtor
        if a is empset: return _Factory(b)
        if b is empset: return _Factory(a)
        if a is uniset or b is uniset: return _Factory(uniset)
        return _Factory(lambda line: a(line) or b(line))

    def __invert__(self):  # 补集
        f = self.filtor
        if f is uniset: return _Factory(empset)
        if f is empset: return _Factory(uniset)
        return _Factory(lambda line: not f(line))
    # '''
    # 一个问题:
    #     已知:
    #         对于 None < 10 , 由于 None 无法与 int 进行比较, 故判断结果为 False
    #     那么:
    #         ~ (None < 10) 的判断结果应该是什么?
    #     答案:
    #         True
    #     解释
    #         任何时候, 两个互为补集的集合的并集都应该是全集.
    # '''
    
    def __sub__(self, factory):  # 差集
        return self & (~ factory)


class _Filter():

    def __init__(self, fields):
        object.__setattr__(self, 'fields', fields)
    
    def __setattr__(self, key, value): raise SetAttrError('_Filter是不可变对象')

    def __getitem__(self, field):
        fields = list(self.fields)
        fields.append(field)
        return _Filter(fields=tuple(fields))

    def _FetchData(self, line):
        for key in self.fields:
            line = line[key]
        return line

    def _GetData(self, line):
        try:
            return self._FetchData(line)
        except:
            return None

    def __lt__(self, obj):
        def filtor(line):
            try:
                return self._FetchData(line) < obj
            except: return False
        return _Factory(filtor)
    
    def __le__(self, obj):
        def filtor(line):
            try:
                return self._FetchData(line) <= obj
            except: return False
        return _Factory(filtor)

    def __gt__(self, obj):
        def filtor(line):
            try:
                return self._FetchData(line) > obj
            except: return False
        return _Factory(filtor)

    def __ge__(self, obj):
        def filtor(line):
            try:
                return self._FetchData(line) >= obj
            except: return False
        return _Factory(filtor)

    def __eq__(self, obj):  # 使用_GetData, 不存在的视为None
        return _Factory(lambda line: self._GetData(line) == obj)

    def __ne__(self, obj):  # 使用_GetData, 不存在的视为None
        return _Factory(lambda line: self._GetData(line) != obj)
    
    def re(self, pattern, flags=0):
        def filtor(line):
            try:
                data = self._GetData(line)
                if data is None:
                    data = ''
                return ReSearch(pattern, data, flags)
            except: return False
        return _Factory(filtor)

    def isin(self, *lis):
        if not lis: return _Factory(empset)
        def filtor(line):
            try:
                return self._GetData(line) in lis
            except: return False
        return _Factory(filtor)
    
    def notin(self, *lis):
        if not lis: return _Factory(uniset)
        def filtor(line):
            try:
                return self._GetData(line) not in lis
            except: return False
        return _Factory(filtor)

    def contain_all(self, *lis):
        if not lis: return _Factory(uniset)
        def filtor(line):
            try:
                data = self._FetchData(line)
                for x in lis:
                    if x not in data:
                        return False
                return True
            except: return False
        return _Factory(filtor)

    def contain_any(self, *lis):
        if not lis: return _Factory(empset)
        def filtor(line):
            try:
                data = self._FetchData(line)
                for x in lis:
                    try:
                        if x in data:
                            return True
                    except: pass
                return False
            except: return False
        return _Factory(filtor)

    def contain_zero(self, *lis):
        if not lis: return _Factory(uniset)
        def filtor(line):
            try:
                data = self._FetchData(line)
                for x in lis:
                    if x in data:
                        return False
                return True
            except: return False
        return _Factory(filtor)

    def custom(self, func):
        def newfunc(line):
            try:
                return func(line)
            except: return False
        return _Factory(newfunc)


class _LaydbColumn():
    def __getattr__(self, field): return _Filter(fields=(field, ))
    def __getitem__(self, field): return _Filter(fields=(field, ))
lc = _LaydbColumn()


class _MakeSlice():
    def __init__(self, func, **param):
        self.func = func
        self.param = param
    def __getitem__(self, key): return self.func(key, **self.param)


class _layline():

    def __init__(self, laydb, _pk):
        object.__setattr__(self, 'laydb', laydb)
        object.__setattr__(self, '_pk', _pk)

    def __setattr__(self, key, value): raise SetAttrError('_layline是不可变对象')

    def update(self, data):
        r = 0
        file = libpath(f"{self.laydb.folder}/{self._pk}.layline")
        if file.exists():
            line = self.laydb.ReadData(file.read_bytes())
            r = 1
        else:
            line = {}
            r = 2
        if not data.get('_pk'): data['_pk'] = self._pk
        line.update(data)
        if self._pk != line['_pk']:
            libpath(f"{self.laydb.folder}/{self._pk}.layline").unlink(missing_ok=True)
            object.__setattr__(self, '_pk', line['_pk'])
        self.laydb + line
        return r

    def delete(self, **param):
        libpath(f"{self.laydb.folder}/{self._pk}.layline").unlink(missing_ok=True)
        return undefined

    def get(self, default=undefined):
        file = libpath(f"{self.laydb.folder}/{self._pk}.layline")
        if file.exists():
            line = self.laydb.ReadData(file.read_bytes())
            return self.laydb.ExeColumns(line)
        elif default is undefined:
            raise KeyError(str(self._pk))
        else:
            return default

    def setdefault(self, default):
        file = libpath(f"{self.laydb.folder}/{self._pk}.layline")
        if file.exists():
            line = self.laydb.ReadData(file.read_bytes())
            return self.laydb.ExeColumns(line)
        else:
            if not default.get('_pk'): default['_pk'] = self._pk
            if self._pk != default['_pk']:
                libpath(f"{self.laydb.folder}/{self._pk}.layline").unlink(missing_ok=True)
                object.__setattr__(self, '_pk', default['_pk'])
            self.laydb + default
            return default


class laydb():
    WriteData = write_pickle
    ReadData = pickle_loads
    path = libpath

    def __init__(self, folder, factory=None, columns=('*', ), _sort=None):
        if type(folder) is _WindowsPath:
            _ObjSet(self, 'folder', folder)
        elif folder[-6:] == '.laydb':
            _ObjSet(self, 'folder', libpath(folder))
        else:
            _ObjSet(self, 'folder', libpath(f"{folder}.laydb"))
        self.folder.mkdir(parents=True, exist_ok=True)
        _ObjSet(self, 'factory', factory or _Factory(uniset))
        _ObjSet(self, 'columns', columns)  # str型 或 tuple型
        _ObjSet(self, '_sort', deepcopy(_sort or {}))
        # {A:True, B:False, ...} 表示 {A:升序, B:降序, ...}
        # 为避免用户将此变量与"order方法"弄混, 使用前缀下划线来隐藏
    
    def __setattr__(self, key, value): raise SetAttrError('laydb是不可变对象')

    def _copy(self, factory=undefined, columns=undefined, _sort=undefined):
        return laydb(
            folder = self.folder,
            factory = self.factory if factory is undefined else factory,
            columns = self.columns if columns is undefined else columns,
            _sort = self._sort if _sort is undefined else _sort,
        )

    def order(self, **rule): return self._copy(_sort={**self._sort, **rule})  # **rule必须放在后面, 才能覆盖旧规则
    def reset_order(self, **rule): return self._copy(_sort=rule)

    def __add__(self, data):
        if type(data) in (dict, ):
            if '_pk' in data:
                _pk = data['_pk']
            else:
                data['_pk'] = _pk = _newpk()
            fpath = f"{self.folder}/{_pk}.layline"
            self.WriteData(fpath, data)
            return _pk
        elif type(data) in (list, deque, tuple):
            for x in data:
                if '_pk' in x:
                    _pk = x['_pk']
                else:
                    x['_pk'] = _pk = _newpk()
                fpath = f"{self.folder}/{_pk}.layline"
                self.WriteData(fpath, x)
            return [x['_pk'] for x in data]
    
    def __setitem__(self, _pk, value):
        if not value.get('_pk'): value['_pk'] = _pk
        if _pk != value['_pk']:
            libpath(f"{self.folder}/{_pk}.layline").unlink(missing_ok=True)
        self.__add__(value)

    def delete(self, **param): return _MakeSlice(self._ExeDelete, **param)
    def _ExeDelete(self, key, _return=None, **param):
        rs = None
        line = None
        if type(key) is slice:
            rs = []
            for line in self._RStyleSlice(key.start, key.stop):
                libpath(f"{self.folder}/{line['_pk']}.layline").unlink(missing_ok=True)
                rs.append(line['_pk'])
        elif type(key) is int:
            try:
                line = self._RStyleIndex(key)
                libpath(f"{self.folder}/{line['_pk']}.layline").unlink(missing_ok=True)
                rs = line['_pk']
            except Exception as e:
                rs = None
                if type(e) is not IndexError:
                    raise e
        if _return == 'last_line':
            return line, rs
        else:
            return rs

    def update(self, data, **param): return _MakeSlice(self._ExeUpdate, data=data, **param)
    def _ExeUpdate(self, key, data, **param):
        if '_pk' in data:
            line, rs = self._ExeDelete(key, _return='last_line')
            if line:
                line.update(data)
                self.__add__(line)
            else:
                self.__add__(data)
            return rs
        elif type(key) is slice:
            rs = []
            for line in self._RStyleSlice(key.start, key.stop):
                line.update(data)
                self.__add__(line)
                rs.append(line['_pk'])
            return rs
        elif type(key) is int:
            try:
                line = self._RStyleIndex(key)
                line.update(data)
                self.__add__(line)
                return line['_pk']
            except Exception as e:
                if type(e) is not IndexError:
                    raise e
                return None

    def __len__(self):
        filtor = self.factory.filtor
        if filtor is empset: return 0
        if filtor is uniset: return len(list(self._LayLineFiles()))
        return len(self[:])
    
    def _LayLineFiles(self):
        for node in self.folder.iterdir():
            if node.is_file():
                if node.suffix == '.layline':
                    yield node

    def _RStyleIndex(self, index):
        '''
        采用R语言的切片风格:
            索引从1开始, 1表示第1个元素, -1表示倒数第1个元素
            切片为双闭区间.
        在此ORM中:
            索引应该 >=1 或 <=-1
            若索引==0则视为1的左边1位
        '''
        filtor = self.factory.filtor
        if filtor is empset: raise IndexError(str(index))
        if index == 0: raise IndexError(str(index))
        if type(index) is not int: raise IndexError(str(index))
        # 读取数据
        lines = []
        i = 0
        for file in self._LayLineFiles():
            try:
                line = self.ReadData(file.read_bytes())
                if filtor(line):
                    lines.append(line)
                    if not self._sort:
                        i += 1
                        if i == index: break
            except Exception as e:
                if type(e) is not FileNotFoundError:
                    raise e
        if self._sort:
            _sort = list(self._sort.items())
            lines = sorted(lines, key=lambda x: [SorPa(x.get(k), v) for k,v in _sort])
        if index > 0:
            return lines[index - 1]
        else:
            return lines[index]

    def _RStyleSlice(self, left, right):
        '''
        采用R语言的切片风格:
            索引从1开始, 1表示第1个元素, -1表示倒数第1个元素
            切片为双闭区间.
        在此ORM中:
            索引应该 >=1 或 <=-1
            若索引==0则视为1的左边1位
        '''
        if left is not None and -1 < left < 0: return []
        if right is not None and 0 <= right < 1: return []
        if left is not None and right is not None:
            if left >= 0 and right >= 0 and floor(right) < ceil(left): return []
            if left < 0 and right < 0 and floor(right) < ceil(left): return []
        filtor = self.factory.filtor
        if filtor is empset: return []
        # 读取数据
        lines = []
        for file in self._LayLineFiles():
            try:
                line = self.ReadData(file.read_bytes())
                if filtor(line):
                    lines.append(line)
            except Exception as e:
                if type(e) is not FileNotFoundError:
                    raise e
        if not lines: return []
        if self._sort:
            _sort = list(self._sort.items())
            lines = sorted(lines, key=lambda x: [SorPa(x.get(k), v) for k,v in _sort])
        total = len(lines)
        if left is not None:
            if left < 0: left = total + left + 1
            left = max(0, ceil(left) - 1)
        if right is not None:
            if right < 0: right = total + right + 1
            right = max(0, floor(right))
        lines = lines[left: right]
        return lines

    def ExeColumns(self, data):
        if '*' in self.columns: return data
        columns = self.columns
        if type(data) is list:
            return [{k:x.get(k) for k in columns} for x in data]
        return {k:data.get(k) for k in columns}

    def __getitem__(self, key):
        typ = type(key)
        if typ is _Factory: return self._copy(factory=self.factory & key)
        if typ is slice: return self.ExeColumns(self._RStyleSlice(key.start, key.stop))
        if typ is int: return self.ExeColumns(self._RStyleIndex(key))
        if typ is str: return _layline(self, key)
        if typ is tuple: return self._copy(columns=key)



'''
项目介绍
    layDB 的加密版，使用 AES-CBC-256 算法加密用户数据。

已实现的功能
    ● laydb已实现的所有功能
    ● 数据加密保存
    ● 可以使用空密码 (使用空密码时, 数据也是加密保存的)
    ● 修改密码
'''

class laydb_aes(laydb):

    def __init__(self, folder, password=b'', factory=None, columns=('*', ), _sort=None):
        laydb.__init__(self, folder, factory, columns, _sort)
        # 创建根密钥
        RootKey = libpath(f"{self.folder}/RootKey.laykey")
        if not RootKey.exists():
            RootKeyCitext = cbc256(password).encrypt(random_bytes(32), salt_size=8, check_size=8)
            RootKey.write_bytes(RootKeyCitext)
        # 载入根密钥
        if type(password) is dict:
            _ObjSet(self, 'password', password)
        else:
            RootKeyCitext = RootKey.read_bytes()
            RootKeyPltext = cbc256(password).decrypt(RootKeyCitext)  # 一定要从本地文件读取, 这是作为一种校验
            _ObjSet(self, 'password', {'cbctool': cbc256(RootKeyPltext)})

    def _copy(self, factory=undefined, columns=undefined, _sort=undefined):
        return laydb_aes(
            folder = self.folder,
            password = self.password,
            factory = self.factory if factory is undefined else factory,
            columns = self.columns if columns is undefined else columns,
            _sort = self._sort if _sort is undefined else _sort,
        )

    def WriteData(self, fpath, data):  # data: Python对象
        data = pickle_dumps(data)
        data = self.password['cbctool'].encrypt(data, salt_size=8, check_size=0)  # check_size为0, 不然太消耗性能
        return libpath(fpath).write_bytes(data)
    
    def ReadData(self, data):  # type(data) is bytes
        return pickle_loads(self.password['cbctool'].decrypt(data))

    def ChangePassword(self, NewPassword):
        # 写入密钥文件
        RootKey = libpath(f"{self.folder}/RootKey.laykey")
        RootKeyPltext = self.password['cbctool'].password
        RootKeyCitext = cbc256(NewPassword).encrypt(RootKeyPltext, salt_size=8, check_size=8)
        RootKey.write_bytes(RootKeyCitext)
        # 读取密钥文件
        RootKeyCitext = RootKey.read_bytes()
        RootKeyPltext = cbc256(NewPassword).decrypt(RootKeyCitext)  # 一定要从本地文件读取, 这是作为一种校验
        self.password['cbctool'] = cbc256(RootKeyPltext)  # 使所有关联实例都得到修改
        return True
