从 汉化通用 导入 _关键词参数中转英, _反向注入

from sqlalchemy.engine import Connection, Engine, Result

Connection.执行 = Connection.execute
Connection.关闭 = Connection.close
Engine.连接 = Engine.connect
Result.取一行 = Result.fetchone
Result.取全部 = Result.fetchall


from sqlalchemy.orm.scoping import scoped_session

scoped_session.添加 = scoped_session.add
scoped_session.提交 = scoped_session.commit
scoped_session.删除 = scoped_session.delete
scoped_session.执行 = scoped_session.execute
scoped_session.获取 = scoped_session.get
scoped_session.查询 = scoped_session.query
scoped_session.刷新 = scoped_session.refresh
scoped_session.回滚 = scoped_session.rollback


from sqlalchemy.schema import Column

_列关键词参数字典 = {
    '自增' : 'autoincrement',
    '默认值' : 'default',
    '文档' : 'doc',
    '键' : 'key',
    '索引' : 'index',
    '信息' : 'info',
    '可为空' : 'nullable',
    '更新时' : 'onupdate',
    '主键' : 'primary_key',
    '服务器_默认值' : 'server_default',
    '服务器_更新时' : 'server_onupdate',
    '引述' : 'quote',
    '唯一' : 'unique',
    '系统' : 'system',
    '备注' : 'comment',
    # '名称' : 'name',  # ？
}

类 〇列(Column):
    """表示数据库表中的一列.
    
    前两个位置参数是 '名称' (可省略) 和 '类型', 关于其余位置参数的信息待补充.
    """
    套路 __init__(分身, *参数々, **关键词参数々):
        关键词参数々 = _关键词参数中转英(关键词参数々, _列关键词参数字典)
        super().__init__(*参数々, **关键词参数々)

    套路 引用(分身, 列):
        返回 分身.references(列)

    套路 追加外键(分身, 外键):
        分身.append_foreign_key(外键)

_反向注入(〇列, Column)


from sqlalchemy.orm.relationships import RelationshipProperty

类 〇关系属性(RelationshipProperty):
    """Describes an object property that holds a single item or list
    of items that correspond to a related database table.
    """
    套路 __init__(分身,
                  参数,
                  中间表=空,
                  主表连接=空,
                  中间表连接=空,
                  外键々=空,
                  使用列表=空,
                  排序依据=空,
                  反向引用=空,
                   **关键词参数々
    ):  # 尚有其他关键词参数, 暂未列出
        super().__init__(参数,
                         secondary=中间表,
                         primaryjoin=主表连接,
                         secondaryjoin=中间表连接,
                         foreign_keys=外键々,
                         uselist=使用列表,
                         order_by=排序依据,
                         backref=反向引用,
                         **关键词参数々)

    # merge, cascade, ...

_反向注入(〇关系属性, RelationshipProperty)


from sqlalchemy.sql.operators import ColumnOperators

类 〇列运算符(ColumnOperators):
    """定义列元素的布尔、比较和其他运算符.
    """

    套路 不同于(分身, 他者):
        返回 分身.is_distinct_from(他者)
    
    套路 非不同于(分身, 他者):
        返回 分身.is_not_distinct_from(他者)
    
    套路 拼接(分身, 他者):  # ？
        返回 分身.concat(他者)
    
    套路 貌似(分身, 他者, 转义=空):
        返回 分身.like(他者, 转义)
    
    套路 貌似_不分大小写(分身, 他者, 转义=空):
        返回 分身.ilike(他者, 转义)
    
    套路 在其中(分身, 他者):
        返回 分身.in_(他者)
    
    套路 不在其中(分身, 他者):
        返回 分身.not_in(他者)

    套路 不像(分身, 他者, 转义=空):
        返回 分身.not_like(他者, 转义)
    
    套路 不像_不分大小写(分身, 他者, 转义=空):
        返回 分身.not_ilike(他者, 转义)

    套路 是_(分身, 他者):
        返回 分身.is_(他者)
    
    套路 不是_(分身, 他者):
        返回 分身.is_not(他者)
    
    套路 开头是(分身, 他者, **关键词参数々):
        """关键词参数有 '转义' 和 '自动转义'."""
        如果 '转义' 在 关键词参数々:
            关键词参数々['escape'] = 关键词参数々.弹出('转义')
        如果 '自动转义' 在 关键词参数々:
            关键词参数々['autoescape'] = 关键词参数々.弹出('自动转义')
        返回 分身.startswith(他者, **关键词参数々)
    
    套路 结尾是(分身, 他者, **关键词参数々):
        """关键词参数有 '转义' 和 '自动转义'."""
        如果 '转义' 在 关键词参数々:
            关键词参数々['escape'] = 关键词参数々.弹出('转义')
        如果 '自动转义' 在 关键词参数々:
            关键词参数々['autoescape'] = 关键词参数々.弹出('自动转义')
        返回 分身.endswith(他者, **关键词参数々)
    
    套路 包含(分身, 他者, **关键词参数々):
        """关键词参数有 '转义' 和 '自动转义'."""
        如果 '转义' 在 关键词参数々:
            关键词参数々['escape'] = 关键词参数々.弹出('转义')
        如果 '自动转义' 在 关键词参数々:
            关键词参数々['autoescape'] = 关键词参数々.弹出('自动转义')
        返回 分身.contains(他者, **关键词参数々)
    
    套路 匹配(分身, 他者, **关键词参数々):
        返回 分身.match(他者, **关键词参数々)
    
    套路 正则匹配(分身, 模式, 标志々=空):
        返回 分身.regexp_match(模式, 标志々)
    
    套路 正则替换(分身, 模式, 替换为, 标志々=空):
        返回 分身.regexp_replace(模式, 替换为, 标志々)
    
    套路 降序(分身):
        返回 分身.desc()
    
    套路 升序(分身):
        返回 分身.asc()
    
    套路 空值优先(分身):
        返回 分身.nulls_first()
    
    套路 空值最后(分身):
        返回 分身.nulls_last()
    
    套路 对照(分身, 对照):  # ？
        返回 分身.collate(对照)
    
    套路 介于(分身, 左值, 右值, 对称=假):
        返回 分身.between(左值, 右值, 对称)
    
    套路 去重(分身):  # ？
        返回 分身.distinct()
    
    套路 任意_(分身):
        返回 分身.any_()
    
    套路 全部_(分身):
        返回 分身.all_()

_反向注入(〇列运算符, ColumnOperators)


from sqlalchemy.orm.query import Query

类 〇查询(Query):

    @property
    套路 语句(分身):
        返回 分身.statement

    # subquery
    # cte
    # label
    # as_scalar
    # scalar_subquery
    # selectable
    # ...

    套路 获取(分身, id):
        返回 分身.get(id)

    # ...
    # correlate
    # ...

    套路 筛选(分身, *标准):
        返回 分身.filter(*标准)
    
    套路 筛选_依据(分身, **关键词参数々):
        返回 分身.filter_by(**关键词参数々)
    
    套路 排序_依据(分身, *条件):
        返回 分身.order_by(*条件)
    
    套路 分组_依据(分身, *条件):
        返回 分身.group_by(*条件)
    
    套路 满足(分身, 标准):
        返回 分身.having(标准)
    
    套路 并(分身, *查询):
        返回 分身.union(*查询)
    
    套路 并_全部(分身, *查询):
        返回 分身.union_all(*查询)
    
    套路 交(分身, *查询):
        返回 分身.intersect(*查询)
    
    套路 交_全部(分身, *查询):
        返回 分身.intersect_all(*查询)
    
    套路 除外(分身, *查询):
        返回 分身.except_(*查询)
    
    套路 除外_全部(分身, *查询):
        返回 分身.except_all(*查询)
    
    套路 连接(分身, 目标, *属性々, **关键词参数々):
        返回 分身.join(目标, *属性々, **关键词参数々)
    
    套路 外连接(分身, 目标, *属性々, **关键词参数々):
        返回 分身.outerjoin(目标, *属性々, **关键词参数々)
    
    套路 重置连接点(分身):
        返回 分身.reset_joinpoint()
    
    套路 选择自(分身, *对象):
        返回 分身.select_from(*对象)
    
    套路 切片(分身, 起, 止):
        返回 分身.slice(起, 止)
    
    套路 设限(分身, 限值):
        返回 分身.limit(限值)
    
    套路 偏移(分身, 偏移量):
        返回 分身.offset(偏移量)
    
    套路 去重(分身, *表达式):
        返回 分身.distinct(*表达式)

    套路 全部(分身):
        返回 分身.all()
    
    套路 第一条(分身):
        返回 分身.first()
    
    套路 一条或没有(分身):
        返回 分身.one_or_none()
    
    套路 一条(分身):
        返回 分身.one()
    
    套路 计数(分身):
        返回 分身.count()
    
    套路 删除(分身, 同步会话="evaluate"):
        返回 分身.delete(synchronize_session=同步会话)
    
    套路 更新(分身, 值々, 同步会话="evaluate", 更新参数々=空):
        返回 分身.update(值々, synchronize_session=同步会话,
                        update_args=更新参数々)

_反向注入(〇查询, Query)

