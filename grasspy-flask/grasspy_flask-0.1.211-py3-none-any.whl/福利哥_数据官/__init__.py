导入 福利哥_数据官.sqlalchemyhack
从 福利哥_数据官.sqlalchemyhack 导入 〇列 为 _〇列
从 福利哥_数据官.sqlalchemyhack 导入 〇关系属性
导入 flask_sqlalchemy
从 flask_sqlalchemy 导入 Pagination, BaseQuery, SQLAlchemy
导入 sqlalchemy
从 sqlalchemy 导入 and_ 为 与_
从 sqlalchemy 导入 not_ 为 非_
从 sqlalchemy 导入 or_ 为 或_
从 sqlalchemy 导入 func 为 函数
从 汉化通用 导入 _关键词参数中转英, _反向注入

# 聚合函数
函数.计数 = 函数.count
函数.平均值 = 函数.avg
函数.最大值 = 函数.max
函数.最小值 = 函数.min
函数.求和 = 函数.sum

# 利用猴子补丁解决表名问题
def __NameMetaMixin_init__(cls, name, bases, d):
        if flask_sqlalchemy.model.should_set_tablename(cls):
            if '__表名__' in cls.__dict__:
                cls.__tablename__ = cls.__表名__
            else:
                cls.__tablename__ = flask_sqlalchemy.model.camel_to_snake_case(cls.__name__.removeprefix('〇'))

        super(flask_sqlalchemy.model.NameMetaMixin, cls).__init__(name, bases, d)

        # __table_cls__ has run at this point
        # if no table was created, use the parent table
        if (
            '__tablename__' not in cls.__dict__
            and '__table__' in cls.__dict__
            and cls.__dict__['__table__'] is None
        ):
            del cls.__table__

flask_sqlalchemy.model.NameMetaMixin.__init__ = __NameMetaMixin_init__


类 〇分页操作(Pagination):

    @property
    套路 查询对象(分身):
        返回 分身.query
    
    @property
    套路 页码(分身):
        "当前页码"
        返回 分身.page
    
    @property
    套路 每页条目数(分身):
        返回 分身.per_page
    
    @property
    套路 总条目数(分身):
        返回 分身.total
    
    @property
    套路 当前页条目数(分身):
        返回 分身.items

    @property
    套路 总页数(分身):
        返回 分身.pages
    
    套路 上一页(分身, 错误输出=假):  # errou_out ?
        返回 分身.prev(错误输出)
    
    @property
    套路 上一页码(分身):
        返回 分身.prev_num
    
    @property
    套路 有上一页(分身):
        返回 分身.has_prev
    
    套路 下一页(分身, 错误输出=假):  # errou_out ?
        返回 分身.next(错误输出)
    
    @property
    套路 有下一页(分身):
        返回 分身.has_next

    @property
    套路 下一页码(分身):
        返回 分身.next_num

    # iter_pages

_反向注入(〇分页操作, Pagination)


类 〇基本查询(BaseQuery):

    套路 获取或404(分身, id, 描述=空):  # ident - identity?
        返回 分身.get_or_404(id, 描述)
    
    套路 第一条或404(分身, 描述=空):
        返回 分身.first_or_404(描述)
    
    套路 分页(分身, 页码=空, 每页条目数=空, 错误输出=真, 每页最多条目数=空):
        返回 分身.paginate(page=页码, per_page=每页条目数, error_out=错误输出,
                          max_per_page=每页最多条目数)

_反向注入(〇基本查询, BaseQuery)


类 〇数据官(SQLAlchemy):
    """本类用于 SQLAlchemy 与一个或多个福利哥应用的集成

    """
    〇列 = _〇列

    关系 = 〇关系属性

    套路 __init__(分身, 应用=空, 使用原生统一码=真, 会话选项々=空,
                  元数据=空, 查询类=〇基本查询,
                  模型类=flask_sqlalchemy.Model, 引擎选项々=空):
        super().__init__(app=应用, use_native_unicode=使用原生统一码,
                         session_options=会话选项々, metadata=元数据,
                         query_class=查询类, model_class=模型类,
                         engine_options=引擎选项々)
        分身.〇模型 = 分身.Model
        分身.〇字符串 = 分身.String
        分身.〇文本 = 分身.Text
        # 分身.〇统一码 = 分身.Unicode
        # 分身.〇统一码文本 = 分身.UnicodeText
        分身.〇整数 = 分身.Integer
        # 分身.〇小整数 = 分身.SmallInteger
        # 分身.〇大整数 = 分身.BigInteger
        分身.〇浮点数 = 分身.Float
        分身.〇日时 = 分身.DateTime
        分身.〇日期 = 分身.Date
        分身.〇时间 = 分身.Time
        分身.〇大二进制 = 分身.LargeBinary
        分身.〇枚举 = 分身.Enum
        分身.〇布尔值 = 分身.Boolean
        # 分身.〇间隔 = 分身.Interval
        分身.文本 = 分身.text  # 例如用于 查询.筛选_依据(文本('-发布时间'))
        分身.〇外键 = 分身.ForeignKey
        分身.会话 = 分身.session
        分身.应用 = 分身.app
        # 分身.〇表 = 分身.Table

    """ 套路 〇列(分身, 字段类型, *参数々, **选项々):
        选项字典 = {
            '主键' : 'primary_key',
            '自增' : 'autoincrement',
            '可为空' : 'nullable',
            '唯一' : 'unique',
            '默认值' : 'default',
        }
        选项々 = _关键词参数中转英(选项々, 选项字典)
        列 = 分身.Column(字段类型, *参数々, **选项々)
        列.降序 = 列.desc
        列.包含 = 列.contains
        返回 列 """

    """ 套路 关系(分身, 模型, **选项々):
        如果 '反向引用' 在 选项々:
            选项々['backref'] = 选项々.弹出('反向引用')
        返回 分身.relationship(模型, **选项々) """

    套路 反向引用(分身, 名称, **关键词参数々):
        """关键词参数同 '关系' """
        关系关键词参数字典 = {
            '中间表' : 'secondary',
            '主表连接' : 'primaryjoin',
            '中间表连接' : 'secondaryjoin',
            '外键々' : 'foreign_keys',
            '使用列表' : 'uselist',
            '排序依据' : 'order_by',  # 其他暂未列出
        }
        关键词参数々 = _关键词参数中转英(关键词参数々, 关系关键词参数字典)
        返回 分身.backref(名称, **关键词参数々)

    @property
    套路 元数据(分身):
        返回 分身.metadata

    # create_scoped_session
    # create_session

    def make_declarative_base(self, model, metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.
        """
        if not isinstance(model, sqlalchemy.orm.decl_api.DeclarativeMeta):
            model = sqlalchemy.ext.declarative.declarative_base(
                cls=model,
                name='Model',
                metadata=metadata,
                metaclass=flask_sqlalchemy.model.DefaultMeta
            )

        # if user passed in a declarative base and a metaclass for some reason,
        # make sure the base uses the metaclass
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, 'query_class', None):
            model.query_class = self.Query

        model.查询 = model.query = flask_sqlalchemy._QueryProperty(self)
        return model

    套路 初始化应用(分身, 应用):
        """此回调函数用于以该数据库的设置初始化一个应用
        """
        返回 分身.init_app(应用)

    # apply_pool_defaults
    # apply_driver_hacks

    @property
    套路 引擎(分身):
        返回 分身.engine

    套路 创建连接器(分身, 应用=空, 绑定=空):
        返回 分身.make_connector(app=应用, bind=绑定)

    套路 获取引擎(分身, 应用=空, 绑定=空):
        返回 分身.get_engine(app=应用, bind=绑定)

    # create_engine
    # get_app
    # get_tables_for_bind
    # get_binds

    套路 创建所有表(分身, 绑定='__all__', 应用=空):
        分身.create_all(bind=绑定, app=应用)
    
    套路 删除所有表(分身, 绑定='__all__', 应用=空):
        分身.drop_all(bind=绑定, app=应用)

    套路 反射(分身, 绑定='__all__', 应用=空):
        分身.reflect(bind=绑定, app=应用)

_反向注入(〇数据官, SQLAlchemy)