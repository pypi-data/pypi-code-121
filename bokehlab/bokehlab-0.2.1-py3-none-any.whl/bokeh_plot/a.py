def parse(*args, color=None, legend=None):
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
        elif isinstance(y, pd.DataFrame):
            if legend is None:
                legend = y.columns.values
            x, y = y.index.values, y.T.values
        elif isinstance(y, pd.Series):
            x, y = y.index.values, y.values
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
    if isinstance(legend, (list, tuple)):
        if len(legend) != n:
            raise ValueError(f'len(legend)={len(legend)}; legend should either be a string or a list/tuple/ndarray of length {n}')
        legends = legend
    elif isinstance(legend, np.ndarray):
        if legend.shape != (n,):
            raise ValueError(f'legend.shape={legend.shape}; legend shape should be ({n},)')
        if not isinstance(legend[0], str):
            raise ValueError(f'legend={legend}; legend elements should be strings')
        legends = legend
    elif isinstance(legend, str):
        legends = [legend] * n
    elif legend is None:
        legends = [None] * n
    else:
        raise ValueError(f'legend={legend}; it should either be a string or a list/tuple/ndarray of length {n}')
    qu = []
    for (x, y, spec), color, legend in zip(tr, colors, legends):
        style, _color = parse_spec(spec)
        if _color != 'a':
            color = _color
        qu.append((x, y, style, color, legend))
    return qu

def test_parser():

