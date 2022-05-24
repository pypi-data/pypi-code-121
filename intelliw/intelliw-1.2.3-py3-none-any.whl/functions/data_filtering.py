def filter_by_condition(data, cfg):
    """
    Filter data by condition, drop row if conditional column is None.

    condition is in json format:
    {
        "op": [     // 外层条件关系 and 或 or
            "and"
        ],
        "terms": [  // 外层条件 list
            {
                "op": "and", // 内层条件关系 and 或 or
                "items": [   // 内层条件 list
                    {
                        "code": "engName", // 字段 code
                        "col_num": 0,
                        "type": "COMPARE", // 字段类型：STRING,NUMBER,ENUM,DATE,BOOLEAN,COMPARE
                        "op": "gt",        // 操作符：eq-等于 neq-不等于 lt-小于 gt-大于 elt-小于等于 egt-大于等于 leftlike-左包含 rightlike-右包含 like-包含 in-在…之内 nin-不在…之内
                        "value": "123"     // 比较的值
                    }
                ]
            }
        ]
    }

    :param data:
    :param cfg: cfg['condition']
    :return:
    """
    condition_str = cfg['condition']
    import json
    condition = json.loads(condition_str)

    # key: code, val: index
    meta = {}
    for i, item in enumerate(data['meta']):
        meta[item['code']] = i

    result = []
    for row in data['result']:
        if _conditional_column_is_none(meta, row, condition):
            continue
        if _evaluate_row(meta, row, condition):
            result.append(row)

    data['result'] = result
    return data


def _conditional_column_is_none(meta: dict, row: list, condition) -> bool:
    """
    weather conditional column is none

    :return: True if conditional column is None
    """
    terms = condition['terms']
    for term in terms:
        for item in term['items']:
            if row[meta[item['code']]] is None:
                return True
    return False


def _evaluate_row(meta: dict, row: list, condition) -> bool:
    """
    evaluate result_row by condition

    :param meta: key: code, val: index
    :param row: row of data been evaluated by condition
    :param condition:  condition
    :return: True if result_row meets condition or False if not
    """
    terms = condition['terms']
    term_ops = condition['op']
    term_op = None
    current = None
    for i, term in enumerate(terms):
        if term_op is None:
            current = _evaluate_term(term, meta, row)
        elif term_op == 'and':
            current = current and _evaluate_term(term, meta, row)
        elif term_op == 'or':
            current = current or _evaluate_term(term, meta, row)
        else:
            raise ValueError('invalid op: {}'.format(term_op))
        if i < len(term_ops):
            term_op = term_ops[i]

    return current


def _evaluate_term(term, meta, row) -> bool:
    current = None
    op = term['op']
    for item in term['items']:
        if current is None:
            current = _evaluate_item(item, meta, row)
            continue
        if op == 'and':
            current = current and _evaluate_item(item, meta, row)
            if not current:
                return False
        elif op == 'or':
            current = current or _evaluate_item(item, meta, row)
        else:
            raise ValueError('invalid op: {}'.format(op))
    return current


def _evaluate_item(item, meta, row) -> bool:
    op = item['op']
    _type = item['type']
    val = _to_type(_type, row[meta[item['code']]])
    target = item['value']
    # eq-等于 neq-不等于 lt-小于 gt-大于 elt-小于等于 egt-大于等于 leftlike-左包含 rightlike-右包含 like-包含 in-在…之内 nin-不在…之内
    if op == 'eq':
        return val == _to_type(_type, target)
    elif op == 'neq':
        return val != _to_type(_type, target)
    elif op == 'lt':
        return val < _to_type(_type, target)
    elif op == 'gt':
        return val > _to_type(_type, target)
    elif op == 'elt':
        return val <= _to_type(_type, target)
    elif op == 'egt':
        return val >= _to_type(_type, target)
    elif op == 'leftlike':
        val = str(val)
        target = str(target)
        return val.startswith(target)
    elif op == 'rightlike':
        val = str(val)
        target = str(target)
        return val.endswith(target)
    elif op == 'like':
        val = str(val)
        target = str(target)
        return val.__contains__(target)
    elif op == 'in':
        keys = list(map(lambda x: _to_type(_type, x), str(target).split(',')))
        return keys.__contains__(val)
    elif op == 'nin':
        keys = list(map(lambda x: _to_type(_type, x), str(target).split(',')))
        return not keys.__contains__(val)
    elif op == 'null':
        return val is None or val == ''
    elif op == 'notnull':
        return val is not None or val != ''
    else:
        raise ValueError('invalid op: {}'.format(op))


def _to_type(_type, val):
    if _type == 'ENUM':
        return str(val)
    elif _type == 'NUMBER':
        if isinstance(val, int):
            return val
        elif isinstance(val, float):
            return val
        else:
            return eval(str(val))
    elif _type == 'BOOLEAN':
        if isinstance(val, bool):
            return val
        else:
            if str(val) == 'True' or str(val) == 'true' or val == 1 or val == '1':
                return True
            else:
                return False
    else:
        if isinstance(val, str):
            return val
        return str(val) if str(val) else None



