from pprint import pprint
import inspect
import heapq
# 参考 https://docs.python.org/3/library/typing.html#typing.Generator
from typing import Dict, Any, List, Tuple, Generator, Union
import random
import re
import timeit
from collections.abc import Iterable
import hashlib
import pickle


def get_func_para(func, del_para=None, add_para: dict = None):
    """提取函数的参数和默认值, 没有默认值设为 None
    比如可以用于设定 TaskDB.result 的例子

    Args:
        func (list, function): 单/多个函数组成的列表, 后面函数出现一样的参数会覆盖前面的默认值
        del_para (set, list, optional): 删除不想看到返回的参数
        add_para (dict, optional): 增加想补充的参数和值, 会覆盖原始值, 不会被 del_para 删除

    Returns:
        dict: 所有函数修剪后的参数和默认值
    """
    paras = {}
    func = func if isinstance(func, list) else [func]
    del_para = set(del_para) if del_para else set()
    add_para = add_para if add_para else {}
    for f in func:
        fullargspec = inspect.getfullargspec(f)
        defaults = fullargspec.defaults if fullargspec.defaults else []
        defaults = [None] * (len(fullargspec.args) - len(defaults)) + list(defaults)
        paras.update({k: v for k, v in zip(fullargspec.args, defaults) if k not in del_para})
    paras.update(add_para)
    return paras


def cover_dict(new_para: dict, default_para: dict, allow_new=False):
    """使用 new_para 中的健值对递归覆盖 default_para 中的值, 遇到非 dict 就不再递归而直接覆盖, 出现类型不一样也会直接覆盖
    比如可以用于新参数覆盖旧参数 (注意因为失误导致的参数覆盖)

    Args:
        new_para (dict): 
        default_para (dict): 被覆盖的, 注意还需要原来的值就要 copy.deepcopy(default_para)
        allow_new (bool): 是否能 让 new_para 出现 default_para 中没有的 key, 能的话就直接加入 default_para

    Returns:
        dict: default_para
    """
    for k, v in new_para.items():
        if k not in default_para:
            if not allow_new:
                raise f'构建了默认参数中没有的参数: {k} not in {set(default_para)}'
            else:
                default_para[k] = v
            continue
        if isinstance(v, dict) and isinstance(default_para[k], dict):
            cover_dict(v, default_para[k], allow_new)
        else:
            default_para[k] = v
    return default_para


def get(key, obj, default=None):
    """
    递归从dict/list/tuple中取值, 以list的形式，以避免中括号取值数量不灵活的问题
    :param key: list/tuple/int/str; list表示递归取值
    :param obj: dict/list/tuple
    :param default: 寻找不到后返回的默认值
    :return:
    """
    key = key if isinstance(key, list) else [key]
    if len(key) == 0:
        return default
    for i in key:
        try:
            obj = obj[i]
        except:
            obj = default
            break
    return obj


def put(key, obj, default=None, delete=False):
    """
    递归在dict/list中放值, 以list的形式，以避免中括号放值数量不灵活的问题
    :param key: list/tuple/int/str; list表示递归放值. 空list会返回 ellipsis
    :param obj: dict/list
    :param default: 放的内容, 会覆盖原有值. 如果路径key路径上没有会构建, 仅限于dict类型
    :param delete: bool; 是否删除而不是放置对应的值
    :return: default or ellipsis or 删除的值
    """
    key = key if isinstance(key, list) else [key]
    if len(key) == 0:
        return ...
    for i in key[:-1]:
        try:
            obj = obj[i]
        except:
            obj = obj.setdefault(i, {})
    if delete:
        default = obj[key[-1]]
        del obj[key[-1]]
    else:
        obj[key[-1]] = default
    return default


def merge_dict(dict_L: List[Dict], union=True, new_dict=None):
    """递归求多个字典的并/交集, 多个字典的v类型不一样(除了None)会使用第1个 dict 的值, 如果不存在或为None则优先向后取

    Args:
        dict_L (List[Dict]): list 中的非 dict 元素会被剔除
        union (bool): 是否求并集, 否则交集
        new_dict (dict, optional): 递归专用, 不能赋值

    Returns:
        dict: new_dict
    """
    new_dict = {} if new_dict is None else new_dict
    dict_L = [i for i in dict_L if isinstance(i, dict)]
    if union:
        set_key = set().union(*dict_L)
    else:
        set_key = set(dict_L[0]).intersection(*dict_L[1:])
    for k in set_key:
        v_L = [d.get(k) for d in dict_L]
        if set(type(v) for v in v_L) <= {dict, type(None)}:
            merge_dict(v_L, union=union, new_dict=new_dict.setdefault(k, {}))
        else:
            new_dict[k] = v_L[0]
            for v in v_L:
                if v is not None:
                    new_dict[k] = v
                    break
    return new_dict


def opt_value_dict(dict1, dict2, opt=lambda v1, v2: v1-v2, new_dict=None):
    """递归求2个字典值的操作值结果, opt操作没有异常才有结果
    如果递归后的 dict1 和 dict2 有一个类型是dict另一个不是, 那么会将是dict的递归然后全部和另一个不是的求opt
    这里的 opt 默认计算的是 dict1 - dict2

    Args:
        dict1 (dict, Any): 
        dict2 (dict, Any): 
        opt (dict, function): 输入 (v1, v2) 返回 计算结果. 如果是 dict 就和 dict1/dict2 一起递归到 非dict(function)
        new_dict (dict, optional): 递归专用, 不能赋值

    Returns:
        dict: new_dict
    """
    new_dict = {} if new_dict is None else new_dict
    for k in (set(dict1) if isinstance(dict1, dict) else set()) | (set(dict2) if isinstance(dict2, dict) else set()):
        v1 = dict1.get(k) if isinstance(dict1, dict) else dict1
        v2 = dict2.get(k) if isinstance(dict2, dict) else dict2
        if type(v1) == dict or type(v2) == dict:
            opt_value_dict(v1, v2, opt[k] if isinstance(opt, dict) else opt, new_dict=new_dict.setdefault(k, {}))
        else:
            try:
                new_dict[k] = opt(v1, v2)
            except:
                ...
    return new_dict


def any_value_dict(dict1, opt=lambda v1, v2: v1 and v2, start_v=True):
    """深度遍历递归求1个字典内部相邻值的操作值结果, opt操作没有异常才更新结果
    这里的 opt 默认计算的是 dict1 中的所有值是不是都是 True

    Args:
        dict1 (dict): 
        opt (dict, function): 输入 (start_v, v) 返回 计算结果. 如果是 dict 就和 dict1 一起递归到 非dict(function)
            v 依次是深度遍历递归的值
        start_v (Any): 初始值, 后面每次更新它

    Returns:
        Any: start_v
    """
    for k, v in dict1.items():
        if type(v) == dict:
            start_v = any_value_dict(v, opt[k] if isinstance(opt, dict) else opt, start_v=start_v)
        else:
            try:
                start_v = opt(start_v, v)
            except:
                ...
    return start_v


def arg_extreme_dict(d: Dict[Any, Dict], dv_key=None, dv_reverse=True, allow_type=None, ban_type=None, traverse_d=None,
                     result=None, root=None):
    """给d中的每个v排序, v中递归的每个元素都排序(只取最大值或最小值), 排序结果的极值用d的k表示
    d中的每个v会取并集key计算, 如果一个dv没有相应的key或为None就不参与极值获取

    Args:
        d (Dict[Any, Dict]): 双层字典, 第二层的每个字典构造格式保持一致, 只允许值不一样或者不存在某些key
        dv_key (dict, function, optional): d中v的每个值使用的排序function, 输入是 (d的k,递归后v值) 对, 输出可排序值
            输入 function 类型就是统一针对所有v的方法
        dv_reverse (dict, bool, optional): d中v的每个值取最大值还是最小值, 默认都是True最大值, 使用dict可针对每个v值选择顺序(不在dict中的还是默认值)
        allow_type (set, list, optional): d中v中的值允许排序的类型, 默认见代码
        ban_type (set, list, optional): d中v中的值不允许排序的类型, 使用这个 allow_type 会失效. 使用时建议加入 dict
        traverse_d (dict, optional): 默认是d中所有v的并集, 用于确定排序对象有哪些k
        result (dict, optional): 用于递归存储结果, 不可以赋值
        root (list, optional): 用于递归存储路径, 不可以赋值

    Returns:
        dict: result
    """
    allow_type = {int, float} if allow_type is None else set(allow_type)
    ban_type = {} if ban_type is None else set(ban_type)
    result = {} if result is None else result
    root = [] if root is None else root
    traverse_d = merge_dict(list(d.values())) if traverse_d is None else traverse_d  # 默认排序对象
    for k, v in traverse_d.items():
        result[k] = {}
        type_v = type(v)
        if (len(ban_type) == 0 and type_v not in allow_type) or (len(ban_type) > 0 and type_v in ban_type):  # 不是允许的类型
            if type_v is dict:  # 是dict就递归
                arg_extreme_dict(d, dv_key=dv_key, dv_reverse=dv_reverse, allow_type=allow_type, ban_type=ban_type,
                                 traverse_d=traverse_d[k], result=result[k], root=root + [k])
        else:
            root_ = root + [k]
            key = dv_key if inspect.isfunction(dv_key) else get(root_, dv_key, lambda t: t[1])  # 排序方式
            reverse = dv_reverse if isinstance(dv_reverse, bool) else get(root_, dv_reverse, True)  # 最大还是最小值排序
            sort_ = heapq.nlargest if reverse else heapq.nsmallest
            result[k] = sort_(1, [(k1, get(root_, v1))  # 出现错误 IndexError: list index out of range 可能是因为加入了排序不了的类型, 比如 None
                              for k1, v1 in d.items() if get(root_, v1) is not None], key=key)[0][0]
    return result


def dict_to_pair(dict1: dict, root=None) -> Generator[Tuple[List, Any], None, None]:
    """深度遍历递归返回所有(k_L,v)对, 遇到非空dict就会递归, 否则作为value返回

    Args:
        dict1 (dict): 
        root (list, optional): 用于递归存储路径, 不可以赋值

    Yields:
        Generator[Tuple[List, Any], None, None]: ([k,..],value),..
    """
    root = [] if root is None else root
    for k, v in dict1.items():
        if type(v) == dict and v:
            yield from dict_to_pair(v, root=root + [k])
        else:
            yield (root + [k], v)


def pair_to_dict(traversed_pair: List[Tuple[List, Any]]) -> dict:
    """所有(k_L,v)对依次还原为dict

    Args:
        traversed_pair (List[Tuple[List, Any]]): ([k,..],value),..

    Returns:
        dict: dict1
    """
    dict1 = {}
    for k_L, v in traversed_pair:
        d = dict1
        for k in k_L[:-1]:
            d = d.setdefault(k, {})
        d[k_L[-1]] = v
    return dict1


def recursion_stat(doc: dict, stat: dict, key_stat=None, len_stat=None, content_stat=None, _len_sum=True, _type=True):
    """
    递归统计mongo字典doc中每个属性出现的次数，以及出现属性类型、特殊长度、内容的次数
    如果出现list并其中元素是dict，那么这一条数据list中不同dict的计数会叠加
    list中嵌套list不会再递归，其他情况会一直递归到非dict/list/tuple变量为止
    key_stat中的s也可以针对{list,tuple}类型的v, 会对v中{float,int,str}的值当{值:None}来处理, 就相当于list中元素是dict

    :param doc: dict; 一条mongodb数据，普通json可能出现关键词重合统计错误问题，比如$开头
    :param stat: dict; 统计结果
    :param key_stat: None or {k:{k:{s,..}/[s,..]/None/func,..},..}; 如果k在其中出现则统计v出现的次数或不统计长度或内容，None表示不统计
        list递归dict则当list不存在，dict中k/s首位是$表示路径到这个k为止，路径最后k的v可以是dict/list/tuple变量，但不会统计v出现次数
        s：$^v表示不统计默认内容出现次数，$^l表示不统计默认长度出现次数，$*l表示统计所有长度出现次数，$*v表示统计所有v出现次数
            $l:{i,..} 表示统计某些长度i出现次数, $v:{v,..} 表示统计某些内容v出现次数
            $.l:func(len(v)) 表示统计某些长度出现次数, $.v:func(v) 表示统计某些内容出现次数
                func方法传入长度或内容,返回None或代号,None表示不统计,长度代号会自动加$,内容代号会自动加$_
            优先级: $*l > $l > $.l > 默认统计, 默认统计见代码
            $*key 表示默认匹配任何key, 它的值是dict, 必须要装下级别的key, 递归的时候会带入. 优先级低于一样的key
        例子：
        key_stat = {
            'paperwithcode': {
                'code': {
                    'frame': {'$*v'},
                    'official': {'$*v'},
                    '$l': set(range(10)),
                    '$.l': lambda l: f'{l // 10}0-{l // 10}9' if l < 100 else f'{l // 100}00-{l // 100}99',
                }
            },
            '期刊分区': {
                'JCR分区': {'$*v'}, 
                '$*key': {'综述': {'$*v'}},
            },
        }
    :param len_stat: None or set; 默认统计value长度, 为None则默认见代码, 不想统计可赋值 set()
    :param content_stat: None or set or dict; 默认统计内容value (会针对类型匹配,例如1和1.0不同), 为None则默认见代码, 不想统计可赋值 set()
        因为 {True, 1, False, 0} == {1, 0} 所以当出现这种冲突建议使用 dict {type:{值,..},..}
    :param _len_sum: bool; 是否统计 $len_sum
    :param _type: bool; 是否统计 $type
    :return: stat
        $times: int; 属性出现次数
        $len_sum: int; 如果属性值属于{dict, list, tuple, str}则统计长度总和
        $expand: dict; 如果属性值是dict或list嵌套dict则递归进入内部统计出现情况
        $type: dict; 统计属性值出现各种类型的次数
        $i: int; 如果属性值属于{dict, list, tuple, str}则统计长度i出现的次数
        $_s: int; 如果属性值不属于{dict, list, tuple}则统计内容s出现的次数
        $len: dict; key为 $i 的对象
        $value: dict; key为 $_s 的对象
        $list: dict; 形式类似于 $expand, 但是针对于{list,tuple}类型v中的{float,int,str}, $list中key就是值
        $species: $expand or $list 中key出现的次数, 大于1才记录
    """
    if key_stat is None:
        key_stat = {}
    # 默认需要统计的特殊长度、内容
    if len_stat is None:
        len_stat = {0}  # 默认统计长度
    if content_stat is None:
        content_stat = {  # 默认统计内容
            None, False, True, 0, 1, -1, 'None', 'null', 'false', 'true', 'False', 'True', '0', '1', '-1',
        }
    # content_stat 改造为字典, 用于针对类型匹配
    if type(content_stat) == set:
        content_stat_ = {}
        for i in content_stat:
            content_stat_.setdefault(type(i), set()).add(i)
        content_stat = content_stat_
    # 开始统计
    for k, v in doc.items():
        stat.setdefault(k, {'$times': 0})
        if isinstance(v, dict):
            expand = stat[k].setdefault('$expand', {})
            if k in key_stat and not isinstance(key_stat[k], set):  # 首位不能是$
                ks = key_stat[k]
            else:  # 当 key_stat[k] 为 set 类型时无效, 因为错误认为v不是dict才有v或l的统计
                ks = key_stat['$*key'] if '$*key' in key_stat else {}
            recursion_stat(v, expand, ks, len_stat, content_stat, _len_sum, _type)
            if len(expand) > 1:
                expand['$species'] = len(expand) - 1  # 种数
        elif type(v) in {list, tuple}:
            expand = expand_list = None
            for i in v:
                if isinstance(i, dict):
                    expand = stat[k].setdefault('$expand', {})
                    if k in key_stat and not isinstance(key_stat[k], set):  # 首位不能是$
                        ks = key_stat[k]
                    else:
                        ks = key_stat['$*key'] if '$*key' in key_stat else {}
                    recursion_stat(i, expand, ks, len_stat, content_stat, _len_sum, _type)
                elif type(i) in {float, int, str}:
                    expand_list = stat[k].setdefault('$list', {})
                    ks = key_stat[k] if k in key_stat else (key_stat['$*key'] if '$*key' in key_stat else {})
                    recursion_stat({i: None}, expand_list, ks, set(), set(), _len_sum, _type)
            # 种数
            if expand is not None and len(expand) > 1:
                expand['$species'] = len(expand) - 1
            if expand_list is not None and len(expand_list) > 1:
                expand_list['$species'] = len(expand_list) - 1
        else:
            s = False
            v_ = v
            if k in key_stat:
                if '$*v' in key_stat[k] or ('$v' in key_stat[k] and v in key_stat[k]['$v']):
                    s = True
                elif '$.v' in key_stat[k]:
                    v_ = key_stat[k]['$.v'](v)
                    if v_ is not None:
                        s = True
                    else:
                        v_ = v
                elif '$^v' not in key_stat[k] and type(v) in content_stat and v in content_stat[type(v)]:
                    s = True
            elif type(v) in content_stat and v in content_stat[type(v)]:
                s = True
            if s:
                stat[k].setdefault('$value', {}).setdefault(f'$_{v_}', 0)
                stat[k]['$value'][f'$_{v_}'] += 1
        if type(v) in {dict, list, tuple, str}:
            if _len_sum:
                stat[k].setdefault('$len_sum', 0)
                stat[k]['$len_sum'] += len(v)
            s = False
            v_ = len(v)
            if k in key_stat:
                if '$*l' in key_stat[k] or ('$l' in key_stat[k] and len(v) in key_stat[k]['$l']):
                    s = True
                elif '$.l' in key_stat[k]:
                    v_ = key_stat[k]['$.l'](len(v))
                    if v_ is not None:
                        s = True
                    else:
                        v_ = len(v)
                elif '$^l' not in key_stat[k] and len(v) in len_stat:
                    s = True
            elif len(v) in len_stat:
                s = True
            if s:
                stat[k].setdefault('$len', {}).setdefault(f'${v_}', 0)
                stat[k]['$len'][f'${v_}'] += 1
        stat[k]['$times'] += 1
        if _type:
            stat[k].setdefault('$type', {}).setdefault(f'${type(v)}', 0)
            stat[k]['$type'][f'${type(v)}'] += 1
    return stat


def replace(pattern, repl_f, string, count=0):
    '''
    正则表达式字符串替换, 可以对待替换字符串进行函数操作
    :param pattern: str; 待替换字符的正则匹配
    :param repl_f: function or str; 如果为function则参数是被替换的字符串
    :param string: str; 替换对象
    :param count: int; 替换前几个?
    :return:
    '''
    if isinstance(repl_f, str):
        return re.sub(pattern=pattern, repl=repl_f, string=string, count=count)
    if count <= 0:
        count = len(string) * 2 + 1  # replace('|1', lambda s: '2', '111')
    span_L = [(0, 0)]
    string_split_L = []
    for i in re.finditer(pattern, string):
        if count <= 0:
            break
        else:
            count -= 1
        span = i.span()
        string_split_L.append(string[span_L[-1][1]: span[0]])
        span_L.append(span)
    string_split_L.append(string[span_L[-1][1]:])
    span_L = span_L[1:]
    string_L = [string_split_L[0]]
    for i, (s, e) in enumerate(span_L):
        string_L.append(repl_f(string[s: e]))
        string_L.append(string_split_L[i + 1])
    return ''.join(string_L)


def get_obj_sha512(x, ignore_type=False, out=None):
    """获取一个对象的sha512值, 递归判断不受指针影响, 无序类型改变顺序不影响值
    冲突概率: https://en.wikipedia.org/wiki/Birthday_problem#Probability_table

    Args:
        x (_type_): 由 可str化的有序类型 / 无序类型(set和dict) 构成
        ignore_type (bool, optional): 是否忽略除无序类型以外的类型(类型全变None), 等于只看遍历后的str值是否一致
        out (list, optional): 用于递归,不可修改

    Returns:
        str, list: sha512, x的深度优先遍历结果
    """
    if out is None:
        out = []
        root = True
    else:
        root = False
    type_x = type(x)
    if type_x == set:
        out.append(type_x)
        x = sorted(x, key=lambda t: pickle.dumps(t))
    elif type_x == dict:
        out.append(type_x)
        x = sorted(x.items(), key=lambda t: pickle.dumps(t[0]))
    # 类型忽略处理
    elif ignore_type:
        out.append(None)  # 加入这个使得单一嵌套情况会被区分
    else:
        out.append(type_x)
    # 递归
    if isinstance(x, Iterable) and type_x not in {str, bytes}:
        for i in x:
            get_obj_sha512(i, ignore_type, out)
    else:
        out.append(str(x))
    if root:
        return hashlib.sha512(pickle.dumps(out)).hexdigest(), out


if __name__ == '__main__':
    class c:
        def __init__(self) -> None:
            pass

        @staticmethod
        def f(a, b=2, c=3, **kw):
            pass
    # get_func_para
    print('=' * 10, 'get_func_para')
    print(get_func_para(c), get_func_para(c.f))
    print()

    # cover_dict
    print('=' * 10, 'cover_dict')
    new_para = {'a': [1, 2, {'bb': 2}], 'b': {'c': (1, 2), 'd': 2}}
    default_para = {'a': [4, 2, {'b': 21}], 'b': {'c': (1, 1), 'd': 22, 'e': None}}
    pprint(cover_dict(new_para, default_para))
    new_para['dd'] = {12}
    print('allow_new:', cover_dict(new_para, default_para, allow_new=True))
    print()

    # arg_extreme_dict
    print('=' * 10, 'arg_extreme_dict')
    epoch = {
        str(i): {
            i2: {
                i3: random.randint(1, 100) for i3 in ['P', 'R', 'F1']
            } for i2 in ['train', 'dev', 'test']
        } for i in range(5)
    }
    put(['5', 'train'], epoch, {'P': 30, 'A': 1, 'a': 123})
    print('put-delete:', put(['5', 'train', 'a'], epoch, delete=True))
    # epoch = {
    #     '0': {'dev': {'evaluate': None},
    #           'test': {'evaluate': {'MAP': 0.11008076900138042,
    #                                 'NDCG': 0.23014383925192927,
    #                                 'bpref': 0.5968450000000048,
    #                                 'macro-F1': 0.10884098853570322,
    #                                 'macro-P': 0.20855,
    #                                 'macro-R': 0.07363544070065223}},
    #           'train': {'evaluate': {'MAP': 0,
    #                                  'NDCG': 0,
    #                                  'bpref': 0,
    #                                  'macro-F1': 0,
    #                                  'macro-P': 0,
    #                                  'macro-R': 0},
    #                     'model': {'acc': 0, 'loss': 1e+38}}},
    #     '1': {'train': {'model': {'acc': 0.9903333136013576,
    #                               'loss': 2.2860701941308523}}}
    # }
    print('原始值:')
    pprint(epoch)
    print('极值:')
    pprint(arg_extreme_dict(epoch, dv_reverse=True, ban_type=[dict, type(None)], dv_key=lambda t: -t[1]))
    print()

    # merge_dict / opt_value_dict / any_value_dict
    print('=' * 10, 'merge_dict / opt_value_dict / any_value_dict')
    dict1 = {1: {1: None, 3: 4, 5: 7, 9: 9}, 2: [1, 2], 3: 10}
    dict2 = {1: {1: 2, 3: None, 5: 6, 6: 6}, 3: {4: 1, 5: 2}}
    print('union_dict:', merge_dict([dict1, dict2, dict2]))
    print('intersection_dict:', merge_dict([dict1, dict2, dict2], False))
    ret = opt_value_dict(opt_value_dict(dict1, dict2), None, opt=lambda v1, v2: v1 > 4)
    print('opt_value_dict:', ret)
    print('any_value_dict:', any_value_dict(ret))
    print()

    # dict_to_pair / pair_to_dict
    print('=' * 10, 'dict_to_pair / pair_to_dict')
    print('dict_to_pair:', list(dict_to_pair(dict1)))
    print('pair_to_dict:', pair_to_dict(dict_to_pair(dict1)))
    print()

    # get_obj_sha512
    print('=' * 10, 'get_obj_sha512')
    a = {2, 3, 1, (1, 2)}, {1: ('123'), 2: 2}
    b = {2, 3, 1, (1, 2)}, {1: ['123'], 2: 2}
    c = {3, 2, 1, (1, 2)}, {2: 2, 1: ['123']}
    print('速度:', timeit.timeit(lambda: get_obj_sha512(a), number=20000))
    a_ = get_obj_sha512(a, True)
    b_ = get_obj_sha512(b, True)
    print('a==b:', a_[0] == b_[0])
    print('a out:', a_[1])
    print('b out:', b_[1])
    b_ = get_obj_sha512(b, False)
    c_ = get_obj_sha512(c, False)
    print('c==b:', c_[0] == b_[0])
    print('c out:', c_[1])
    print('b out:', b_[1])
