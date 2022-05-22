# coding:utf-8
import bson
from ...backend import db


def to_dict(user, with_info=False, fields=None):
    ret = {'user_id': str(user.id),
           'lut': str(getattr(user, 'lut', None)\
                      or user.info.get('lut') or user.created or ''),
           'created': str(user.created),
           'name': user.name,
           'soft_del': user.soft_del}
    ret['email'] = user.info.get('email')\
                   or user.info.get('orgEmail') or ''
    ret['mobile'] = user.info.get('mobile') or ''
    ret['position_id'] = user.info.get('position_id') or ''
    ret['position_name'] = user.info.get('position_name') or ''
    ret['position_tags'] = user.info.get('position_tags') or []
    ret['position_path'] = user.info.get('position_path') or []
    ret['creator_id'] = user.info.get('creator_id') or ''
    ret['creator_name'] = user.info.get('creator_name') or ''
    ret['role_names'] = user.info.get('role_names') or []
    ret['dingtalk_id'] = user.info.get('dingtalk_id') or ''
    ret['jobnumber'] = user.info.get('jobnumber') or ''
    ret['avatar'] = user.info.get('avatar') or ''

    if with_info:
        ret['info'] = user.info
    if fields is not None:
        ret = {k: v for k, v in ret.items() if k in fields}
    return ret


def list_users(q=None):
    if q:
        if isinstance(q, dict):
            user_list = db.get_list_query(db.User, **q)
        else:
            user_list = dg.get_list_query(db.User, q)
    else:
        user_list = db.get_list_query(db.User, soft_del=False)
    return True, list(map(to_dict, user_list))


def get_user_names(user_ids, soft_del=None):
    filters = {'$in': ['id', user_ids]}
    if soft_del is not None:
        filters['soft_del'] = soft_del
    user_list = db.get_list_query(db.User, **filters)
    return True, dict(map(lambda u: (str(u.id), u.name), user_list))


def get_user_info_dict(user_ids):
    user_ids = list(filter(lambda x: bson.objectid.ObjectId.is_valid(x),
                           user_ids))
    user_list = db.get_list_query(soft_del=False,
                                  **{'$in': ['id', user_ids]})
    return True, dict(map(lambda u: (str(u.id),
                          to_dict(u)),
                     user_list))


def query_users(keyword):
    pass_login = db.get_inst(db.PasswordLogin,
                             username=keyword,
                             soft_del=False)
    if pass_login:
        return list_users(q={'id': pass_login.user_id})
    q = [{'name': keyword},
         {'info.email': keyword},
         {'info.mobile': keyword}]
    if len(keyword) == 12 or len(keyword) == 24:
        q.append({'id': keyword})
    return list_users(q={'$or': q})


def query_by_info(query_type, query_value):
    q = {'soft_del': False}
    if query_type in ['email',
                      'mobile',
                      'jobnumber',
                      'position_name']:
        q["info.%s" % query_type] = query_value
    elif query_type in ['role_name',
                        'position_tag']:
            q['info.%ss' % query_type] = query_value
    return db.get_list_query(db.User, **q)


def get_by_info(query_type, query_value):
    user = query_by_info(query_type, query_value).first()
    return (True, to_dict(user) if user else None)


def enable_user(user_id):
    user = db.get_inst(db.User, id=user_id)
    if not user:
        return False, "用户不存在"
    if user.soft_del == True:
        user.soft_del = False
        user.save()
    return True, to_dict(user)


def disable_user(user_id):
    user = db.get_inst(db.User, id=user_id)
    if not user:
        return False, "用户不存在"
    if user.soft_del == False:
        user.soft_del = True
        user.save()
    return True, to_dict(user)


def update_user(user_id, **kw):
    user = db.get_inst(db.User, id=user_id)
    if not user:
        return False, "用户不存在"
    if 'name' in kw:
        user.name = kw.pop('name')
    user.info = {**user.info, **kw}
    user.save()
    return True, to_dict(user)


def get_audit_log_desc(log_entry):
    ret = {'log_id': str(log_entry.id),
           'created': log_entry.created.isoformat(),
           'user_id': log_entry.user_id,
           'editor_id': log_entry.editor_id,
           'editor_name': log_entry.editor_name}
    coll_map = {
        'user_perm': '权限信息',
        'user': '基本信息',
        'password_login': '登录信息'
    }
    field_map = {
        'name': '名字',
        'roles': '角色',
        'perms': '权限',
        'position_id': '职位',
        'granted_positions': '授权的数据范围',
        'soft_del': '有效性',
        'info': '具体信息',
        'lut': ''
    }
    msg = "修改了用户的%s" % coll_map.get(log_entry.collection_name,
                                        log_entry.collection_name)
    fields_desc = []
    for f in log_entry.fields[:3]:
        if field_map.get(f):
            fields_desc.append(field_map.get(f, f))
    if fields_desc:
        msg += ', 字段包括(但不限于)%s等' % (','.join(fields_desc))
    ret['msg'] = msg
    return ret


def get_user_audit_log(user_id, **kw):
    desc = kw.get('desc', True)
    cursor_id = kw.get('cursor_id') or None
    limit = kw.get('limit', 10)
    log_objs, last_id = db.UserAuditLog._iter(threshold=cursor_id,
                                              filters={'user_id': user_id},
                                              desc=True,
                                              limit=limit)
    ret = [get_audit_log_desc(i) for i in log_objs]
    return True, ret


def create_user(name, **info):
    user = db.User(name=name,
                   info=info)
    user.save()
    return user
