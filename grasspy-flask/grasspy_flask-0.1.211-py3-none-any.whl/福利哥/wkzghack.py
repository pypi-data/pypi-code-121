导入 re
从 汉化通用 导入 _反向注入
# 导入 types

导入 werkzeug.routing
从 werkzeug.exceptions 导入 abort
从 werkzeug.utils 导入 redirect
从 werkzeug.security 导入 generate_password_hash
从 werkzeug.security 导入 check_password_hash
从 werkzeug.utils 导入 secure_filename
从 werkzeug.datastructures 导入 *
from werkzeug._internal import _missing


werkzeug.routing.Map.default_converters = {
    "default": werkzeug.routing.UnicodeConverter,
    "string": werkzeug.routing.UnicodeConverter,
    "字符串": werkzeug.routing.UnicodeConverter,
    "any": werkzeug.routing.AnyConverter,
    "任意": werkzeug.routing.AnyConverter,
    "path": werkzeug.routing.PathConverter,
    "路径": werkzeug.routing.PathConverter,
    "int": werkzeug.routing.IntegerConverter,
    "整数": werkzeug.routing.IntegerConverter,
    "float": werkzeug.routing.FloatConverter,
    "浮点数": werkzeug.routing.FloatConverter,
    "uuid": werkzeug.routing.UUIDConverter,
}

# 利用猴子补丁让路由规则支持中文字符
werkzeug.routing._rule_re = re.compile(
    r"""
    (?P<static>[^<]*)                           # static rule data
    <
    (?:
        (?P<converter>[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)   # converter name
        (?:\((?P<args>.*?)\))?                  # converter arguments
        \:                                      # variable delimiter
    )?
    (?P<variable>[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*)        # variable name
    >
    """,
    re.VERBOSE,
)


套路 中止(状态, *参数々, **关键词参数々):
    abort(状态, *参数々, **关键词参数々)

套路 重定向(位置, 状态码=302, 〇响应=空):
    返回 redirect(位置, code=状态码, Response=〇响应)

套路 生成密码哈希值(密码, 方法="pbkdf2:sha256", 盐值长度=16):
    返回 generate_password_hash(密码, method=方法, salt_length=盐值长度)

套路 检查密码哈希值(密码哈希值, 密码):
    返回 check_password_hash(密码哈希值, 密码)

套路 安全文件名(文件名):
    文件名 = 文件名.encode('unicode-escape').decode().replace('\\u', '')
    返回 secure_filename(文件名)


# werkzeug datastructures.py
套路 遍历多值项(映射):
    返回 iter_multi_items(映射)

类 〇不可变列表混入(ImmutableListMixin):

    套路 追加(分身, 元素):
        分身.append(元素)
    
    套路 移除(分身, 元素):
        分身.remove(元素)
    
    套路 扩充(分身, 可迭代对象):
        分身.extend(可迭代对象)
    
    套路 插入(分身, 位置, 值):
        分身.insert(位置, 值)
    
    套路 弹出(分身, 位置=-1):
        分身.pop(位置)
    
    套路 反转(分身):
        分身.reverse()
    
    套路 排序(分身, 键=空, 逆=假):
        分身.sort(key=键, reverse=逆)

_反向注入(〇不可变列表混入, ImmutableListMixin)


类 〇不可变字典混入(ImmutableDictMixin):
    
    @classmethod
    套路 从键创建(本类, 键々, 值=空):
        返回 本类.fromkeys(键々, 值)
    
    套路 设默认值(分身, 键, 默认值=空):
        分身.setdefault(键, 默认值)
    
    套路 更新(分身, *参数々, **关键词参数々):
        分身.update(*参数々, **关键词参数々)
    
    套路 弹出(分身, 键, 默认值=空):
        分身.pop(键, 默认值=空)
    
    套路 弹出项(分身):
        分身.popitem()
    
    套路 清空(分身):
        分身.clear()

_反向注入(〇不可变字典混入, ImmutableDictMixin)


类 〇不可变多值字典混入(ImmutableMultiDictMixin):
    
    套路 增加(分身, 键, 值):
        分身.add(键, 值)
       
    套路 弹出项列表(分身):
        分身.popitemlist()

    套路 弹出列表(分身, 键):
        分身.poplist(键)
    
    套路 设置列表(分身, 键, 新列表):
        分身.setlist(键, 新列表)
    
    套路 设置列表默认值(分身, 键, 默认值列表=空):
        分身.setlistdefault(键, 默认值列表)

_反向注入(〇不可变多值字典混入, ImmutableMultiDictMixin)


类 〇更新字典混入(UpdateDictMixin):
    
    套路 设默认值(分身, 键, 默认值=空):
        返回 分身.setdefault(键, 默认值)

    套路 弹出(分身, 键, 默认值=_missing):
        返回 分身.pop(键, 默认值)

〇更新字典混入.清空 = UpdateDictMixin.clear
〇更新字典混入.弹出项 = UpdateDictMixin.popitem
〇更新字典混入.更新 = UpdateDictMixin.update

_反向注入(〇更新字典混入, UpdateDictMixin)


类 〇类型转换字典(TypeConversionDict):
    
    套路 获取(分身, 键, 默认值=空, 类型=空):
        返回 分身.get(键, default=默认值, type=类型)

_反向注入(〇类型转换字典, TypeConversionDict)


类 〇不可变类型转换字典(ImmutableTypeConversionDict):
    
    套路 拷贝(分身):
        返回 分身.copy()

_反向注入(〇不可变类型转换字典, ImmutableTypeConversionDict)


类 〇多值字典(MultiDict):

    套路 增加(分身, 键, 值):
        分身.add(键, 值)
    
    套路 获取列表(分身, 键, 类型=空):
        返回 分身.getlist(键, 类型)
    
    套路 设置列表(分身, 键, 新列表):
        分身.setlist(键, 新列表)
    
    套路 设默认值(分身, 键, 默认值=空):
        返回 分身.setdefault(键, 默认值)
    
    套路 设置列表默认值(分身, 键, 默认值列表=空):
        返回 分身.setdefault(键, 默认值列表)
    
    套路 项々(分身, 多值=假):
        返回 分身.items(多值)
    
    套路 列表々(分身):
        返回 分身.lists()
    
    套路 值々(分身):
        返回 分身.values()
    
    套路 列表值々(分身):
        返回 分身.listvalues()
    
    套路 拷贝(分身):
        返回 分身.copy()
    
    套路 深拷贝(分身, 备忘录=空):
        返回 分身.deepcopy(备忘录)
    
    套路 转为字典(分身, 扁平=真):
        返回 分身.to_dict(扁平)
    
    套路 更新(分身, 映射):
        分身.update(映射)
    
    套路 弹出(分身, 键, 默认值=_missing):
        返回 分身.pop(键, 默认值)
    
    套路 弹出项(分身):
        返回 分身.popitem()
    
    套路 弹出列表(分身, 键):
        返回 分身.poplist(键)
    
    套路 弹出项列表(分身):
        返回 分身.popitemlist()

_反向注入(〇多值字典, MultiDict)


类 〇有序多值字典(OrderedMultiDict):

    套路 键々(分身):
        返回 分身.keys()
    
    套路 值々(分身):
        返回 分身.values()
    
    套路 项々(分身, 多值=假):
        返回 分身.items(多值)
    
    套路 列表々(分身):
        返回 分身.lists()
    
    套路 列表值々(分身):
        返回 分身.listvalues()

    套路 增加(分身, 键, 值):
        分身.add(键, 值)
    
    套路 获取列表(分身, 键, 类型=空):
        返回 分身.getlist(键, 类型)
    
    套路 设置列表(分身, 键, 新列表):
        分身.setlist(键, 新列表)
    
    套路 设置列表默认值(分身, 键, 默认值列表=空):
        返回 分身.setdefault(键, 默认值列表)
    
    套路 更新(分身, 映射):
        分身.update(映射)
    
    套路 弹出列表(分身, 键):
        返回 分身.poplist(键)

    套路 弹出(分身, 键, 默认值=_missing):
        返回 分身.pop(键, 默认值)
    
    套路 弹出项(分身):
        返回 分身.popitem()
    
    套路 弹出项列表(分身):
        返回 分身.popitemlist()

_反向注入(〇有序多值字典, OrderedMultiDict)


类 〇头信息(Headers):

    套路 获取(分身, 键, 默认值=空, 类型=空, 转为字节=假):
        返回 分身.get(键, default=默认值, type=类型, as_bytes=转为字节)
    
    套路 获取列表(分身, 键, 类型=空, 转为字节=假):
        返回 分身.getlist(键, type=类型, as_bytes=转为字节)
    
    套路 获取全部(分身, 名称):
        返回 分身.get_all(名称)

    套路 项々(分身, 小写=假):
        返回 分身.items(小写)

    套路 键々(分身, 小写=假):
        返回 分身.keys(小写)
    
    套路 值々(分身):
        返回 分身.values()

    套路 扩充(分身, *参数々, **关键词参数々):
        分身.extend(*参数々, **关键词参数々)

    套路 移除(分身, 键):
        返回 分身.remove(键)

    套路 弹出(分身, 键=空, 默认值=_missing):
        返回 分身.pop(key=键, default=默认值)
    
    套路 弹出项(分身):
        返回 分身.popitem()

    套路 增加(分身, _键, _值, **键值对):
        分身.add(_键, _值, **键值对)
    
    套路 清空(分身):
        分身.clear()

    套路 设置(分身, _键, _值, **键值对):
        分身.set(_键, _值, **键值对)
    
    套路 设置列表(分身, 键, 值々):
        分身.setlist(键, 值々)
    
    套路 设默认值(分身, 键, 默认值):
        返回 分身.setdefault(键, 默认值)
    
    套路 设置列表默认值(分身, 键, 默认值):
        返回 分身.setlistdefault(键, 默认值)

    套路 更新(分身, *参数々, **关键词参数々):
        分身.update(*参数々, **关键词参数々)

    套路 转为wsgi列表(分身):
        返回 分身.to_wsgi_list()
    
    套路 拷贝(分身):
        返回 分身.copy()
    
_反向注入(〇头信息, Headers)


# ImmutableHeadersMixin
# EnvironHeaders

类 〇合并多值字典(CombinedMultiDict):

    @classmethod
    套路 从键创建(本类, 键々, 值=空):
        本类.fromkeys(键々, 值)

    套路 获取(分身, 键, 默认值=空, 类型=空):
        返回 分身.get(键, default=默认值, type=类型)

    套路 获取列表(分身, 键, 类型=空):
        返回 分身.getlist(键, 类型)

    套路 键々(分身):
        返回 分身.keys()
    
    套路 项々(分身, 多值=假):
        返回 分身.items(多值)

    套路 值々(分身):
        返回 分身.values()
    
    套路 列表々(分身):
        返回 分身.lists()
    
    套路 列表值々(分身):
        返回 分身.listvalues()

    套路 拷贝(分身):
        返回 分身.copy()

    套路 转为字典(分身, 扁平=真):
        返回 分身.to_dict(扁平)

_反向注入(〇合并多值字典, CombinedMultiDict)


类 〇文件多值字典(FileMultiDict):

    套路 增加文件(分身, 名称, 文件, 文件名=空, 内容类型=空):
        分身.add_file(名称, 文件, filename=文件名, content_type=内容类型)

_反向注入(〇文件多值字典, FileMultiDict)


类 〇不可变字典(ImmutableDict):

    套路 拷贝(分身):
        返回 分身.copy()

_反向注入(〇不可变字典, ImmutableDict)


类 〇不可变多值字典(ImmutableMultiDict):

    套路 拷贝(分身):
        返回 分身.copy()

_反向注入(〇不可变多值字典, ImmutableMultiDict)


类 〇不可变有序多值字典(ImmutableOrderedMultiDict):

    套路 拷贝(分身):
        返回 分身.copy()

_反向注入(〇不可变有序多值字典, ImmutableOrderedMultiDict)


# ...


类 〇文件存储(FileStorage):

    套路 __init__(分身, 流=空, 文件名=空, 名称=空, 内容类型=空,
                  内容长度=空, 头信息=空):
        super().__init__(stream=流, filename=文件名, name=名称,
                    content_type=内容类型, content_length=内容长度, headers=头信息)

    @property
    套路 文件名(分身):
        返回 分身.filename
    
    @property
    套路 名称(分身):
        返回 分身.name
    
    @property
    套路 流(分身):
        返回 分身.stream
    
    @property
    套路 头信息(分身):
        返回 分身.headers

    @property
    套路 内容类型(分身):
        返回 分身.content_type
    
    @property
    套路 内容长度(分身):
        返回 分身.content_length
    
    @property
    套路 mime类型(分身):
        返回 分身.mimetype
    
    @property
    套路 mime类型参数々(分身):
        返回 分身.mimetype_params
    
    套路 保存(分身, 目标路径或文件对象, 缓冲区大小=16384):
        分身.save(目标路径或文件对象, 缓冲区大小)
    
    套路 关闭(分身):
        分身.close()

_反向注入(〇文件存储, FileStorage)
