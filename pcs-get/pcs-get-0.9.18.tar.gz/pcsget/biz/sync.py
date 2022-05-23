# -*- coding: utf-8 -*-
import os.path

from requests import Session, Response

from .login import *
from .utils import *


def sync_demand(num):
    """
    请求需求协议集列表，根据需求编号按协议集名称匹配拿到对应需求集id
    :type num: str
    """
    if not is_int(num):
        e("需求编号应该是整型数字！")
        return
    session = prepare_session()
    if session is None:
        return
    response = session.get(
        "http://protocol.client.bigo.inner/get_demand_on_project_version?project_id=3&project_version_id=3")
    r = decode_msg_value(response, "所有需求协议集")
    demands = r['demands']
    for d in demands:
        if num in d['name']:
            sync_demand_protocols(session, d['id'])
            return
    e("未搜索到该需求的协议集合, 请确认协议集名称是否规范（需要包含需求编号和名称）")


def sync_names(names):
    """
    按协议名称同步协议
    :type names: str
    """
    if len(names) == 0:
        e("请输入协议名称！")
        return
    name_list = names.split(',')
    session = prepare_session()
    if session is None:
        return
    path = os.path.abspath(".")
    pkg = detect_package()
    if len(pkg) == 0:
        w("当前路径未检测到合适包名！请CD到类似'/main/java/pcsget/'路径下执行脚本")
        return
    lang = read_config()[K_LANG]
    extension = get_file_extension(lang)
    for n in name_list:
        r = search_single_name(session, n)
        if r is not None:
            code = generate_protocol_code(session, r['id'], lang, r['demand_id'])
            if len(code) > 0:
                save_code_file(path, r['name'], code, pkg, extension)


def sync_dir(path):
    """
    按目录更新已存在的协议
    :type path: str
    """
    session = None
    pkg = None
    actual_target_count = 0
    actual_updated_count = 0
    for p in os.listdir(path):
        dot_file_extension = os.path.splitext(p)[1]
        if dot_file_extension.endswith('.java') or dot_file_extension.endswith('.kt'):
            actual_target_count += 1
            name = os.path.split(p)[1].replace(dot_file_extension, "")
            extension = dot_file_extension.replace(".", "")
            lang = get_lang(extension)
            local_uts = detect_file_update_time(p)
            if len(local_uts) == 0:
                w("协议" + name + "的本地更新时间戳解析失败，放弃更新!")
                continue
            if session is None:
                session = prepare_session()
                if session is None:
                    return
            if pkg is None:
                pkg = detect_package()
                if len(pkg) == 0:
                    w("当前路径未识别到合适包名！请CD到类似'/main/java/a/b/c'路径下允许脚本")
                    return
            r = search_single_name(session, name)
            if r is not None and r['update_time'] != local_uts:
                code = generate_protocol_code(session, r['id'], lang, r['demand_id'])
                if len(code) > 0:
                    # 二次确认更新时间戳，调试时发现源码更新时间戳回和上面协议搜索的事件戳不一致
                    remote_uts = detect_code_update_time(code)
                    if remote_uts != local_uts:
                        save_code_file(path, r['name'], code, pkg, extension)
                        actual_updated_count += 1
    if actual_target_count == 0:
        e("当前目录下未识别到源码文件")
        return
    if actual_updated_count == 0:
        i("远端无协议变更")


def prepare_session():
    """
    生成一个有效session, 未配置时/cookie失效/自动登录失败等异常情况下返回None
    :rtype union(Session, None)
    """
    cfg_dict = read_config()
    session = Session()

    # 读取配置
    token = ""
    session_id = ""
    user = ""
    pw = ""
    if K_TOKEN in cfg_dict:
        token = cfg_dict[K_TOKEN]
    if K_SESSION in cfg_dict:
        session_id = cfg_dict[K_SESSION]
    if K_USER in cfg_dict:
        user = cfg_dict[K_USER]
    if K_PW in cfg_dict:
        pw = cfg_dict[K_PW]
        if len(pw) > 0:
            pw = decrypt(pw)

    if len(token) > 0 and len(session_id) > 0:
        session.cookies['csrftoken'] = token
        session.cookies['sessionid'] = session_id
        if is_session_login(session):
            return session
        else:
            w("当前会话已过期")
            if len(pw) == 0 or len(user) == 0:
                w("未配置用户名或密码，无法触发自动登录.")
                return None
            else:
                r = login(session, user, pw)
                if r:
                    i("登录成功！")
                    return session
                else:
                    e("登录失败！")
                    return None
    elif len(user) > 0 and len(pw) > 0:
        r = login(session, user, pw)
        if r:
            i("登录成功！")
            return session
        else:
            e("登录失败！")
            return None
    else:
        e("请先配置登录凭据！可选配置：1.token(csrftoken)和session(sessionid)  2.user(协议系统用户名)和password(密码)")
        return None
    return None


def generate_protocol_code(session, id, lang, demand_id):
    """
    请求当个协议的源码内容
    :type session: Session
    :type id: int
    :type lang: str
    :type demand_id: int
    :rtype str
    """
    payload = {
        'id': id,
        'lang': lang,
        'demand_id': demand_id,
        'annotation': 0
    }
    response = session.post(
        url='http://protocol.client.bigo.inner/generate_single_protocol/',
        data=json.dumps(payload)
    )
    return decode_msg_value(response, "生成协议源码")


def sync_demand_protocols(session, demand_id):
    """
    请求需求协议集列表，根据需求编号按协议集名称匹配拿到对应需求集id
    :type session: Session
    :type demand_id: int
    """
    response = session.get("http://protocol.client.bigo.inner/get_protocol_on_demand/?id=" + str(demand_id))
    protocols = decode_msg_value(response, "需求协议集")
    if len(protocols) == 0:
        return
    curr_path = os.path.abspath(".")
    package = detect_package()
    if len(package) == 0:
        w("当前路径未检测到合适包名！请CD到类似'/main/java/pcsget/'路径下执行脚本")
        return
    lang = read_config()[K_LANG]
    extension = get_file_extension(lang)
    for p in protocols:
        proto_name = p['proto_name']
        if proto_name.startswith("PSS"):
            continue
        source = generate_protocol_code(session, p['id'], lang, demand_id)
        save_code_file(curr_path, p['proto_name'], source, package, extension)


def search_single_name(session, name):
    """
    按协议名称搜索协议信息
    :type session: Session
    :type name: str
    """
    url = "http://protocol.client.bigo.inner/search_protocol/?proto_name=" \
          + name \
          + "&proto_uri=0&part_uri=&part_svid=&wholeUri=false"
    response = session.get(url=url)
    results = decode_msg_value(response, "搜索")
    if len(results) == 0:
        e("未搜索到指定协议, name=" + name)
        return
    for r in reversed(results):
        if name == r['proto_name']:
            p_id = r['id']
            p_demand = r['demand_list'][0]['id']
            p_update_time = str(r['update_time'])
            return {'id': p_id, 'name': name, 'demand_id': p_demand, 'update_time': p_update_time}
    return None


def decode_msg_value(res, log_tag):
    """
    解析响应json里的msg字段，如果http响应或者业务status非200，则返回
    :type res: Response
    :type log_tag: str
    """
    if res.status_code != 200:
        e(log_tag + "HTTP请求失败, code=" + str(res.status_code))
        return ""
    body = res.json()
    if body['status'] != 200:
        e(log_tag + "响应状态码非200, status=" + body['status'])
        return ""
    msg_value = body['msg']
    if len(msg_value) == 0:
        e(log_tag + "响应内容为空, msg=" + msg_value)
    return msg_value
