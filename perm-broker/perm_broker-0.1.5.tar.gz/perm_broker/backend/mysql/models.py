import logging
import datetime
import bson
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from ... import default

logger = logging.getLogger(__name__)


engine = None

session = None

Base = declarative_base()


def bson_id_gen():
    oid = str(bson.objectid.ObjectId())
    return oid


def model_save(self):
    try:
        if hasattr(self, 'lut'):
            self.lut = datetime.datetime.now()
        session.add(self)
        session.commit()
    except Exception as e:
        session.close()

Base.save = model_save


class User(Base):
    __tablename__ = 'user'

    id = sa.Column(sa.String(length=32), default=bson_id_gen, primary_key=True)
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    name = sa.Column(sa.String(length=32, collation=default.MYSQL_COLLATION))
    state = sa.Column(sa.String(length=32, collation=default.MYSQL_COLLATION), server_default='normal')
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    info = sa.Column(sa.JSON, default={})
    keywords = sa.Column(sa.String(length=4096))


class UserAuditLog(Base):
    __tablename__ = 'user_audit_log'

    id = sa.Column(sa.BIGINT, primary_key=True)
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    user_id = sa.Column(sa.String(length=32))
    collection_name = sa.Column(sa.String(length=32))
    editor_id = sa.Column(sa.String(length=32))
    editor_name = sa.Column(sa.String(length=32, collation=default.MYSQL_COLLATION))
    editor_info = sa.Column(sa.JSON, default={})
    fields = sa.Column(sa.JSON, default=[])
    delta = sa.Column(sa.JSON, default=[])


class PermDesc(Base):
    '''
    权限的描述，用于权限列表的展示，权限的提示等
    '''
    __tablename__ = 'perm_desc'

    id = sa.Column(sa.BIGINT, primary_key=True)
    action = sa.Column(sa.String(length=255))
    effect = sa.Column(sa.String(length=255), default='allow')
    resources = sa.Column(sa.JSON, default=[])
    name = sa.Column(sa.String(length=32))
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    soft_del = sa.Column(sa.Boolean(), default=False, server_default=sa.text('0'))
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class RoleDesc(Base):
    __tablename__ = 'role_desc'

    id = sa.Column(sa.BIGINT, primary_key=True)
    name = sa.Column(sa.String(length=32))
    perms = sa.Column(sa.JSON, default=[])
    granted_positions = sa.Column(sa.JSON, default=[])
    foreign_key = sa.Column(sa.String(length=255))
    info = sa.Column(sa.JSON, default=[])
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class PositionDesc(Base):
    '''
    职位描述，每个用户通过关联职位描述来确定上下级关系和数据集权限
    --------
    name: string, 职位名称
    parent_id: string, 职位的父级职位id
    path: list, 从根节点到当前节点的id路径，包括根节点，不包括当前节点
    position_type: string, 职位的类型，用于区分一些特殊的职位，比如理财顾问
    '''
    __tablename__ = 'position_desc'

    id = sa.Column(sa.BIGINT ,primary_key=True)
    name = sa.Column(sa.String(length=32))
    parent_id = sa.Column(sa.BIGINT)
    path = sa.Column(sa.JSON, default=[])
    position_type = sa.Column(sa.String(length=32))
    foreign_key = sa.Column(sa.String(length=255))
    tags = sa.Column(sa.JSON, default=[])
    info = sa.Column(sa.JSON, default={})
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class UserPerm(Base):
    __tablename__ = 'user_perm'

    id = sa.Column(sa.BIGINT, primary_key=True)
    user_id = sa.Column(sa.String(length=32))
    roles = sa.Column(sa.JSON, default=[])
    perms = sa.Column(sa.JSON, default=[])
    position_id = sa.Column(sa.BIGINT)
    granted_positions = sa.Column(sa.JSON, default=[])
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class LoginRecord(Base):
    __tablename__ = 'login_record'

    id = sa.Column(sa.BIGINT, primary_key=True)
    user_id = sa.Column(sa.String(length=32))
    login_type = sa.Column(sa.String(length=32))
    sid = sa.Column(sa.String(length=255))
    expiration = sa.Column(sa.DateTime, default=datetime.datetime.now)
    info = sa.Column(sa.JSON, default={})
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)


class PasswordLogin(Base):
    __tablename__ = 'password_login'

    id = sa.Column(sa.BIGINT, primary_key=True)
    user_id = sa.Column(sa.String(length=32), nullable=False)
    username = sa.Column(sa.String(length=32), nullable=False)
    password = sa.Column(sa.String(length=32))
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class ResetPasswordRecord(Base):
    __tablename__ = 'reset_password_record'

    id = sa.Column(sa.BIGINT, primary_key=True)
    user_id = sa.Column(sa.String(length=32), nullable=False)
    code = sa.Column(sa.String(length=32), nullable=False)
    query_times = sa.Column(sa.BIGINT, default=0)
    state = sa.Column(sa.String(length=32), default='created')
    info = sa.Column(sa.JSON, default={})
    timestamp = sa.Column(sa.BIGINT, default=lambda: int(time.time()))
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)


class ThirdPartyLogin(Base):
    __tablename__ = 'third_party_login'

    id = sa.Column(sa.BIGINT, primary_key=True)
    login_type = sa.Column(sa.String(length=32), nullable=False)
    user_id = sa.Column(sa.String(length=32), nullable=False)
    ref_id = sa.Column(sa.String(length=255))
    info = sa.Column(sa.JSON, default={})
    soft_del = sa.Column(sa.Boolean(),default=False, server_default=sa.text('0'))
    created = sa.Column(sa.DateTime, default=datetime.datetime.now)
    lut = sa.Column(sa.DateTime, default=datetime.datetime.now)
