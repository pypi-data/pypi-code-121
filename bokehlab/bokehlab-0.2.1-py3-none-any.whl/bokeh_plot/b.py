def parse(*args, color=None, label=None):
    tr = []
    style = '-'
    if len(args) in (1, 2):
        x = Missing()
        if len(args) == 1:
            y = args[0]
        elif isinstance(args[1], str) or \
             isinstance(args[1], (tuple, list)) and len(args[0]) > 0 and \
             isinstance(args[1][0], str):
            y, style = args
        else:
            x, y = args
        if isinstance(y, dict):
            x, y = list(y.keys()), list(y.values())
        tr.extend(parse3(x, y, style))
    elif len(args) % 3 == 0:
        n = len(args)//3
        for h in range(n):
            x, y, style = args[3*h:3*(h+1)]
            tr.extend(parse3(x, y, style))
    n = len(tr)

    # color
    if isinstance(color, (list, tuple)):
        if len(color) != n:
            raise ValueError(f'len(color)={len(color)}; color should either be a string or a tuple of length {n}')
        colors = color
    elif isinstance(color, str):
        colors = [color] * n
    elif color is None:
        colors = 'a'*n
    else:
        raise ValueError(f'color={color}; it should either be a string or a tuple of length {n}')

    # legend
    if isinstance(label, (list, tuple)):
        if len(label) != n:
            raise ValueError(f'len(label)={len(label)}; label should either be a string or a tuple of length {n}')
        labels = label
    elif isinstance(label, str):
        labels = [label] * n
    elif label is None:
        labels = [None] * n
    else:
        raise ValueError(f'label={label}; it should either be a string or a tuple of length {n}')
    qu = []
    try:
        for (x, y, spec, label1), color, label2 in zip(tr, colors, labels):
            style, _color = parse_spec(spec)
            if _color != 'a':
                color = _color
            qu.append((x, y, style, color, label2 if label2 is not None else label1))
    except Exception as e:
        print(e)
        import ipdb; ipdb.set_trace()
        
    return qu

