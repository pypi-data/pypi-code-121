# coding:utf-8
from ...backend import db


def is_logined(req, session):
    user_id = session.get('user_id')

    if not user_id:
        return False
    if getattr(req, 'user', None)\
            and str(req.user.id) == user_id:
        return True
    else:
        user = db.get_inst(db.User, id=user_id, soft_del=False)
        if user:
            req.user = user
            return True
    return False


def login(user, req, session):
    if user and user.soft_del != True:
        session['user_id'] = str(user.id)
        req.user = user
        return True
    return False


def logout(req, session):
    req.user = None
    session.clear()


def record_login(user_id, login_type, sid=None, **info):
    record = db.LoginRecord(user_id=user_id,
                            sid=sid,
                            login_type=login_type,
                            info=info)
    record.save()
    return record


def get_record_desc(record):
    ret = {'time': record.created.isoformat(),
           'record_id': str(record.id),
           'user_id': record.user_id,
           'login_type': record.login_type}
    return ret


def get_user_login_record(user_id, **kw):
    desc = kw.get('desc', True)
    cursor_id = kw.get('cursor_id') or None
    limit = kw.get('limit', 10)
    filters = {'user_id': user_id}
    if cursor_id:
        filters['$lt'] = ['id', cursor_id]
    log_objs = list(db.get_list_query(db.LoginRecord,
                                      order_by='-id',
                                      **filters)\
                    .limit(limit))
    ret = [get_record_desc(i) for i in log_objs]
    return True, ret
