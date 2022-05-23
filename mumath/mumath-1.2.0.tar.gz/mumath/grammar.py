from .context.tokens import *  # builtins.tokenizer does this so why not me
from .node import mml, html, special
from .node.util import clone, traverse
from .util import listify
from itertools import islice, count
from functools import partial, wraps
import xml.etree.ElementTree as ET


# https://github.com/pengbo-learn/python-math-expression-parser

# drawn characters:
# - mi, mn, mo, ms, mspace?, mtext?
# - menclose, mfrac, mroot, msqrt


def diff(tokens, i, attrib=None):
    attrib = attrib if attrib is not None else {}
    # a bit overly optimized, based on the flag value
    # which coincidentally corresponds to the index
    mark = [None, "n", "p", "n p"][tokens[i].flag]

    if mark is not None:
        class_ = attrib.get("class")
        if class_ is None:
            attrib["class"] = mark
        else:
            attrib["class"] = " ".join((class_, mark))
    return attrib


def wrapped(hof):
    # hof = higher order function
    def _hof(func, *args, **kwargs):
        return wraps(func)(hof(func, *args, **kwargs))
    return _hof

partial = wrapped(partial)


def _print(tokens):
    print("".join(tkn.string for tkn in tokens))


def map_get(mapping, key):
    # utility function
    return mapping.property(key, (key, {}))


def nonspace(tokens, i):
    for i, e in enumerate(islice(tokens, i, None), start=i):
        if e.type != SOFT_SPACE: break
    return i


def _string(glyph, tokens, i):
    return tokens[i].string, i+1


def _variant(glyph, tokens, i):
    return tokens[i].variant, i+1


def _isbox(el): return el.tag == "mrow" and len(el) == 1
def _unbox(el): return _unbox(el[0]) if _isbox(el) else el


def number(glyph, tokens, i):
    return mml.mn(tokens[i].string, diff(tokens, i)), i+1

def element(tokens, i, mtype, mapping):
    symbol, attrib = map_get(mapping, tokens[i].variant)
    attrib = diff(tokens, i, attrib)
    return mtype(symbol, attrib), i+1

def identifier(glyph, tokens, i):
    return element(tokens, i, mml.mi, glyph)

def operator(glyph, tokens, i):
    return element(tokens, i, mml.mo, glyph)

def relator(glyph, tokens, i):
    return element(tokens, i, mml.mo, glyph)

def binary_operator(glyph, tokens, i):
    return element(tokens, i, mml.mo, glyph)

def string_literal(glyph, tokens, i):
    return mml.ms(tokens[i].string[1:-1], diff(tokens, i)), i+1

def space(glyph, tokens, i):
    attrib = map_get(glyph, tokens[i].variant)
    return mml.mspace(attrib), i+1

def word(glyph, tokens, i):
    return mml.mi(tokens[i].string), i+1

def comment(glyph, tokens, i):
    el = html.Comment(comment)
    el.text = tokens[i].string[1:].lstrip()
    return el, i+1


def _separator(glyph, tokens, i, ttype, stretch, mapping, attrib):
    i = nonspace(tokens, i)
    if tokens[i].type != ttype:
        raise KeyError
    b, i = _variant(glyph, tokens, i)
    if b == stretch:
        b, i = _variant(glyph, tokens, i)
        attrib["stretchy"] = "true"
    b = mapping[b].property
    return mml.mo(b, **diff(tokens, i-1, attrib)), i


def open_bracket(glyph, tokens, i, **attrib):
    return _separator(glyph, tokens, i, OPEN, r"\left", glyph, attrib)


def close_bracket(glyph, tokens, i, **attrib):
    return _separator(glyph, tokens, i, CLOSE, r"\right", glyph, attrib)


def middle(glyph, tokens, i, **attrib):
    return _separator(glyph, tokens, i, COL_SEP, r"\middle", glyph, attrib)


def no_number(glyph, tokens, i):
    # Singleton object
    return special.NO_NUMBER, i+1


def text(glyph, tokens, i):
    attrib = diff(tokens, i)
    _b, i = open_bracket(glyph, tokens, i+1)

    def stringed(parts):
        def width(k): return f"{round(k/5, 1)}em"

        n = nonspace(parts, 0)
        m = nonspace(reversed(parts), 0)
        # unfortuntely parts[n:-m] doesn't work for m=0
        text = "".join(e.string for e in parts[n:len(parts)-m])

        strings = []
        if n: strings.append(mml.mspace(width=width(n)))
        strings.append(mml.mtext(text))
        if m: strings.append(mml.mspace(width=width(m)))

        return strings


    mrow = mml.mrow(attrib=attrib)

    parts = []
    while i < len(tokens):
        if tokens[i].type == CLOSE:
            mrow.extend(stringed(parts))
            break
        elif tokens[i].type == TEXT_SEP:
            mrow.extend(stringed(parts))
            parts.clear()
            block, i = blocks(glyph, tokens, i+1)
            mrow.extend(block)

            # block may end before getting to the next $
            while tokens[i].type != TEXT_SEP:
                i += 1
        else:
            parts.append(tokens[i])
        i += 1

    _b, i = close_bracket(glyph, tokens, i)

    return mrow, i


def _subsups(glyph, tokens, i):
    subsup = []
    last = SUP
    while i < len(tokens):
        try:
            ttype = tokens[i].type
            if ttype not in {SUP, SUB}:
                break

            node, i = factor(glyph, tokens, i+1)
            if ttype == last:
                subsup.append(mml.none())
            subsup.append(node)
            last = ttype
        except KeyError:
            break

    if last == SUB:  # Must be even
        subsup.append(mml.none())

    return subsup, i



def _scripts(glyph, tokens, i, ttypes):
    scripts = []

    for ttype in ttypes:
        if i < len(tokens) and tokens[i].type == ttype:
            node, i = factor(glyph, tokens, i+1)
        else:
            node, i = mml.none(), i
        scripts.append(node)

    return scripts, i


_subsup = partial(_scripts, ttypes=[SUB, SUP])
_subbsupp = partial(_scripts, ttypes=[SUBB, SUPP])


def prescripts(glyph, tokens, i):
    mms = mml.mmultiscripts()
    mpre = mml.mprescripts()

    if tokens[i].type == PRESCRIPT:
        i += 1

    prescripts, i = _subsups(glyph, tokens, i)

    try:
        # Add binop or relation here?
        node, i = factor(glyph, tokens, i)
        mms.append(node)
    except KeyError:
        # Technically invalid? Graceful save
        mms.append(mpre)
        mms.extend(prescripts)
        return mms, i

    postscripts, i = _subsups(glyph, tokens, i)

    mms.extend(postscripts)
    mms.append(mpre)
    mms.extend(prescripts)

    return mms, i


def multiscripts(glyph, tokens, i, base):
    postscripts, i = _subsups(glyph, tokens, i)

    if len(postscripts) > 2:
        return mml.mmultiscripts([base, *postscripts]), i
    elif len(postscripts) == 2:
        sub, sup = postscripts
        if base.get("movablelimits"):
            if sub.tag == sup.tag == "none":  # slow
                raise KeyError
            elif sub.tag == "none":
                return mml.mover([base, sup]), i
            elif sup.tag == "none":
                return mml.munder([base, sub]), i
            else:
                return mml.munderover([base, *postscripts]), i
        else:
            if sub.tag == sup.tag == "none":  # slow
                raise KeyError
            elif sub.tag == "none":
                return mml.msup([base, sup]), i
            elif sup.tag == "none":
                return mml.msub([base, sub]), i
            else:
                return mml.msubsup([base, *postscripts]), i
    else:
        raise KeyError


def _binargs(glyph, tokens, i):
    hyper, i = product(glyph, tokens, i)
    base, i = product(glyph, tokens, i)

    return [hyper, base], i


def underset(glyph, tokens, i):
    # generalize overset/underset to hyperscript?
    (under, base), i = _binargs(glyph, tokens, i+1)
    return mml.munder([base, under]), i


def overset(glyph, tokens, i):
    (over, base), i = _binargs(glyph, tokens, i+1)
    return mml.mover([base, over]), i


def underover(glyph, tokens, i, base):
    stack, i = _subbsupp(glyph, tokens, i)
    subb, supp = stack

    if subb.tag == supp.tag == "none":  # slow
        raise KeyError
    elif subb.tag == "none":
        return mml.mover([base, supp]), i
    elif supp.tag == "none":
        return mml.munder([base, subb]), i
    else:
        return mml.munderover([base, *stack]), i


def series(glyph, tokens, i):
    def mutate(node, var, n):
        for el in traverse(node):
            if el.text == var.text:
                el.text = str(n)

    def template(expr, var, n):
        node = clone(expr)
        mutate(node, var, n)
        return node

    def _int(el): return int(el.text)

    (sub, sup), i = _subsup(glyph, tokens, i+1)
    expr, i = product(glyph, tokens, i)
    var, _assignment, start = sub
    end = _unbox(sup)

    start, end = map(_int, (start, end))

    mrow = mml.mrow()

    for n in range(start, end):
        mrow.append(template(expr, var, n))
        mrow.append(mml.mo("+"))
    mrow.append(template(expr, var, end))

    return mrow, i


def group(glyph, tokens, i):
    left, i = open_bracket(glyph, tokens, i, stretchy="false")

    group = []
    while i < len(tokens):
        try:
            block, i = blocks(glyph, tokens, i)
            group.extend(block)
            sep, i = middle(glyph, tokens, i)
            group.append(sep)
        except KeyError:
            break
    right, i = close_bracket(glyph, tokens, i, stretchy="false")

    mrow = mml.mrow()

    if left.text and right.text:
        mrow.extend([left, *group, right])
    elif left.text:
        mrow.extend([left, *group])
    elif right.text:
        mrow.extend([*group, right])
    else:
        mrow.extend(group)

    return mrow, i


def class_(glyph, tokens, i):
    name, i = factor(glyph, tokens, i+1)
    node, i = factor(glyph, tokens, i)

    name = "".join(name.itertext()).strip()

    node.set("class", name)

    return node, i


def displaystyle(glyph, tokens, i):
    node, i = factor(glyph, tokens, i+1)

    node.set("displaystyle", "true")

    return node, i


def enclose(glyph, tokens, i):
    attrib = diff(tokens, i)
    variant, i = _variant(glyph, tokens, i)
    node, i = factor(glyph, tokens, i)

    notation = glyph[variant].property

    # good?
    if _isbox(node):
        node.tag = "menclose"
        node.set("notation", notation)
    else:
        node = mml.menclose([node], notation=notation)

    return node, i


def pad(glyph, tokens, i):
    node, i = product(glyph, tokens, i+1)
    node = _unbox(node)

    mpadded = mml.mpadded([node], lspace="0.5em", rspace="0.5em")
    return mpadded, i


def function(glyph, tokens, i):
    symbol, attrib = map_get(glyph, tokens[i].variant)
    return mml.mo(symbol, diff(tokens, i, attrib)), i+1


def variant(glyph, tokens, i):
    variant, i = _variant(glyph, tokens, i)
    node, i = factor(glyph, tokens, i)

    style = glyph[variant].property
    fontable = {"mi", "mn", "mo", "ms", "mtext"}

    for el in traverse(node):
        if el.tag in fontable:
            el.attrib.update(style)

    return node, i


def hat(glyph, tokens, i):
    attrib = diff(tokens, i)
    htype, i = _variant(glyph, tokens, i)
    node, i = factor(glyph, tokens, i)
    node = _unbox(node)

    hat = mml.mo(glyph[htype].property, attrib=attrib)

    mover = mml.mover([node, hat], accent="true")
    return mover, i


def shoe(glyph, tokens, i):
    attrib = diff(tokens, i)
    stype, i = _variant(glyph, tokens, i)
    node, i = factor(glyph, tokens, i)
    node = _unbox(node)

    hat = mml.mo(glyph[stype].property, attrib=attrib)

    mover = mml.munder([node, hat], accent="true")
    return mover, i


def norm(glyph, tokens, i):
    attrib = diff(tokens, i)
    ntype, i = _variant(glyph, tokens, i)
    node, i = product(glyph, tokens, i)
    node = _unbox(node)

    def _bracket(b): return mml.mo(b, stretchy="true", attrib=attrib.copy())

    lb, rb = map(_bracket, glyph[ntype].property)

    norm = mml.mrow([lb, node, rb])
    return norm, i


def sqrt(glyph, tokens, i):
    attrib = diff(tokens, i)
    _, i = _variant(glyph, tokens, i)
    node, i = product(glyph, tokens, i)
    node = _unbox(node)

    msqrt = mml.msqrt([node], attrib=attrib)
    return msqrt, i


def root(glyph, tokens, i):
    attrib = diff(tokens, i)
    _, i = _variant(glyph, tokens, i)
    [root, base], i = _binargs(glyph, tokens, i)

    # can be of the form \root[2+2]{3}
    if len(root) > 1 and root[0].text == "[" and root[-1].text == "]":
        # not pretty
        del root[0]
        del root[-1]

    base = _unbox(base)
    root = _unbox(root)

    mroot = mml.mroot([base, root], attrib=attrib)
    return mroot, i


def _sep(glyph, tokens, i, ttype):
    i = nonspace(tokens, i)
    if tokens[i].type == ttype:
        return i + 1
    raise KeyError


_row_sep = partial(_sep, ttype=ROW_SEP)
_col_sep = partial(_sep, ttype=COL_SEP)


def _row(glyph, tokens, i):
    row = []
    while i < len(tokens):
        try:
            cell, i = blocks(glyph, tokens, i)
            row.append(cell)
            i = _col_sep(glyph, tokens, i)
        except KeyError:
            try:
                # in case of empty cell
                i = _col_sep(glyph, tokens, i)
                row.append([])
            except KeyError:
                break

    row = [mml.mtd(cell) for cell in row]
    return row, i


def _table(glyph, tokens, i):
    table = []
    while i < len(tokens):
        try:
            row, i = _row(glyph, tokens, i)
            table.append(row)
            i = _row_sep(glyph, tokens, i)
        except KeyError:
            break

    table = [mml.mtr(row) for row in table]
    return table, i


def matrix(glyph, tokens, i):
    def _brackets(mtype, lbracket, rbracket):
        if mtype == r"\matrix":
            return lbracket, rbracket
        elif mtype == r"\cases":
            return mml.mo("{", stretchy="true"), None
        else:
            return None, None

    mtype, i = _string(glyph, tokens, i)
    lbracket, i = open_bracket(glyph, tokens, i, stretchy="true")
    table, i = _table(glyph, tokens, i)
    rbracket, i = close_bracket(glyph, tokens, i, stretchy="true")

    left, right = _brackets(mtype, lbracket, rbracket)

    bracketed = []
    if left is not None: bracketed.append(left)
    bracketed.append(mml.mtable(table))
    if right is not None: bracketed.append(right)
    matrix = mml.mrow(bracketed)

    return matrix, i

def _environment(glyph, tokens, i):
    lb, i = open_bracket(glyph, tokens, i)
    mvar, i = _variant(glyph, tokens, i)
    rb, i = close_bracket(glyph, tokens, i)
    return mvar, i


def environment(glyph, tokens, i):
    mvar, i = _environment(glyph, tokens, i+1)
    table, i = _table(glyph, tokens, i)
    i = nonspace(tokens, i)
    assert tokens[i].string == r"\end"
    mvar2, i = _environment(glyph, tokens, i+1)
    assert mvar == mvar2

    def _bracket(b): return mml.mo(b, stretchy="true")

    left, right = map(_bracket, glyph[mvar].property)

    bracketed = []
    if left.text is not None: bracketed.append(left)
    bracketed.append(mml.mtable(table))
    if right.text is not None: bracketed.append(right)
    matrix = mml.mrow(bracketed)


    return matrix, i


def factor(glyph, tokens, i):
    type_map = {
        IDENTIFIER: identifier,
        WORD: word,
        # ENVIRONMENT: identifier,
        NUMBER: number,
        OPERATOR: operator,
        SPACE: space,
        SUB: prescripts,
        SUP: prescripts,
        PRESCRIPT: prescripts,
        UNDERSET: underset,
        OVERSET: overset,
        OPEN: group,
        STRING: string_literal,

        FUNCTION: function,
        LARGEOP: operator,
        OPERATOR: operator,
        HAT: hat,
        SHOE: shoe,
        NORM: norm,
        SQRT: sqrt,
        MATRIX: matrix,
        VARIANT: variant,
        ENCLOSE: enclose,
        CLASS_: class_,
        TEXT: text,
        OPEN: group,
        BEGIN: environment,
        SERIES: series,
        NO_NUMBER: no_number,
        COMMENT: comment,

        FRAC: fraction,
        BINOM: binomial,
        ROOT: root,
        DISPLAYSTYLE: displaystyle,
        PAD: pad,

        BINOP: binary_operator,
        RELATION: relator,
    }

    i = nonspace(tokens, i)

    return type_map[tokens[i].type](glyph, tokens, i)


def scripted(glyph, tokens, i, left):
    type_map = {
        SUB: multiscripts,
        SUP: multiscripts,
        SUBB: underover,
        SUPP: underover,
    }

    i = nonspace(tokens, i)

    return type_map[tokens[i].type](glyph, tokens, i, left)


def product(glyph, tokens, i):
    node, i = factor(glyph, tokens, i)

    if i < len(tokens):
        try:
            node, i = scripted(glyph, tokens, i, node)
        except KeyError:
            pass

    return node, i


def is_space(el):
    if el.tag in {"mtext", "mspace", "maligngroup", "malignmark"}:
        return True
    if el.tag in {"mstyle", "mphantom", "mpadded", "mrow"} and all(map(is_space, el)):
        return True
    return False


EMBELLISHABLE_FIRST = {"msub", "msup", "msubsup", "munder", "mover", "munderover", "mmultiscripts", "mfrac"}
EMBELLISHABLE_ANY = {"mstyle", "mphantom", "mpadded", "mrow"}
def is_embellished(el):
    if el.tag == "mo":
        return True
    if el.tag in EMBELLISHABLE_FIRST and is_embellished(el[0]):
        return True
    if el.tag in EMBELLISHABLE_ANY:
        em = sum(map(is_embellished, el))
        sp = sum(map(is_space, el))
        # There can only be one embellished child; the rest must be space-like
        return em == 1 and em + sp == len(el)
    return False


def _embellish(el):
    if el.tag == "mo" and el.get("form"):
        el.set("form", "prefix")
        el.set("rspace", "0")
    elif el.tag in EMBELLISHABLE_FIRST:
        _embellish(el[0])
    elif el.tag in EMBELLISHABLE_ANY:
        em = sum(map(is_embellished, el))
        sp = sum(map(is_space, el))
        # There can only be one embellished child; the rest must be space-like
        if em == 1 and em + sp == len(el):
            _embellish(next(filter(lambda c: c.tag == "mo", el)))
    else:
        # not an operator
        pass


def term(glyph, tokens, i):
    products = []

    prod, i = product(glyph, tokens, i)
    products.append(prod)

    while i < len(tokens):
        try:
            prod, i = product(glyph, tokens, i)

            if prod.tag == "mrow" and prod[0].text == "(":
                _embellish(products[-1])

            # FIXME
            # if products[-1].get("embellished") and prod.get("grouping"):
            #     embellish(products[-1])

            products.append(prod)

        except KeyError:
            break

    return products, i


def binop(glyph, tokens, i):
    i = nonspace(tokens, i)

    if tokens[i].type != BINOP:
        raise KeyError

    binop, i = binary_operator(glyph, tokens, i)

    try:
        binop, i = scripted(glyph, tokens, i, binop)
    except KeyError:
        pass

    return binop, i


def expression(glyph, tokens, i):
    expression = []

    # Check if first element is binary operator
    # If so, make it a unary operator
    try:
        node, i = binop(glyph, tokens, i)
        node.set("prefix", "true")
        expression.append(node)
    except (KeyError, IndexError):
        pass

    while i < len(tokens):
        try:
            terms, i = term(glyph, tokens, i)
            expression.extend(terms)
            try:
                node, i = binop(glyph, tokens, i)
                expression.append(node)
            except (KeyError, IndexError):
                pass
        except KeyError:
            break

    return expression, i


def _collapse(nodes):
    return mml.mrow(nodes) if len(nodes) > 1 else nodes[0]


def _collapse2(left, right):
    if len(left) == len(right) == 1:
        return [left[0], right[0]]
    else:
        return [mml.mrow(left), mml.mrow(right)]


def over(glyph, tokens, i, left):
    # otype, i = _string(glyph, tokens, i)
    attrib = diff(tokens, i)
    right, i = expression(glyph, tokens, i+1)

    frac = mml.mfrac(_collapse2(left, right), attrib=attrib)

    # unsupported
    # if otype == r"\bover":
    #     frac.set("bevelled", "true")

    return [frac], i


def fraction(glyph, tokens, i):
    attrib = diff(tokens, i)
    args, i = _binargs(glyph, tokens, i+1)
    return mml.mfrac(args, attrib=attrib), i


def choose(glyph, tokens, i, left):
    attrib = diff(tokens, i)
    right, i = expression(glyph, tokens, i+1)

    def _bracket(b): return mml.mo(b, attrib=attrib.copy())

    lb, rb = map(_bracket, "()")
    children = _collapse2(left, right)

    mfrac = mml.mfrac(children, linethickness="0", attrib=attrib.copy())

    return [lb, mfrac, rb], i


def binomial(glyph, tokens, i):
    attrib = diff(tokens, i)
    args, i = _binargs(glyph, tokens, i+1)

    def _bracket(b): return mml.mo(b, attrib=attrib.copy())

    lb, rb = map(_bracket, "()")
    children = _collapse2(*args)

    mfrac = mml.mfrac(args, linethickness="0", attrib=attrib.copy())
    mrow = mml.mrow([lb, mfrac, rb])

    return mrow, i


def relation(glyph, tokens, i, left):
    relation, i = relator(glyph, tokens, i)

    try:
        relation, i = scripted(glyph, tokens, i, relation)
    except KeyError:
        pass

    right, i = expression(glyph, tokens, i)

    return [*left, relation, *right], i


def block_operation(glyph, tokens, i, left):
    type_map = {
        OVER: over,
        CHOOSE: choose,
        RELATION: relation,
    }
    i = nonspace(tokens, i)

    return type_map[tokens[i].type](glyph, tokens, i, left)


def blocks(glyph, tokens, i):
    node, i = expression(glyph, tokens, i)

    while i < len(tokens):
        try:
            node, i = block_operation(glyph, tokens, i, node)
        except KeyError:
            break

    return node, i


def _line(glyph, tokens, i):
    row = []
    while i < len(tokens):
        try:
            cell, i = blocks(glyph, tokens, i)
            row.append(cell)
            if i < len(tokens):
                i = _col_sep(glyph, tokens, i)
        except KeyError as e:
            try:
                # in case of empty cell
                i = _col_sep(glyph, tokens, i)
                row.append([])
            except KeyError:
                break

    left = mml.mtd(style="width:50%;padding:0;")
    right = mml.mtd(style="width:50%;padding:0;")
    row = [left] + [mml.mtd(cell) for cell in row] + [right]
    return row, i


def _equation(glyph, tokens, i):
    # almost identical to _table and _row
    table = []
    while i < len(tokens):
        try:
            row, i = _line(glyph, tokens, i)
            table.append(row)
            if i < len(tokens):
                i = _row_sep(glyph, tokens, i)
        except KeyError:
            break

    table = [mml.mtr(row, columnalign="left") for row in table]
    table = mml.mtable(table, displaystyle="true")
    return table, i


def _equation_number(n):
    cell = mml.mtd(style="padding:0;", columnalign="right")
    padding = mml.mpadded(width="2em")
    cell.append(padding)

    if n is not None:
        equation_attrib = dict(id=f"eqn-{n}", href=f"#eqn-{n}")
        padding.attrib.update(equation_attrib)
        number = mml.mtext(f"({n})")
        padding.append(number)

    return cell


def enumeration(table, counter):
    # mutates table
    for row in table:
        count = True
        for cell in row:
            if special.NO_NUMBER in cell:
                # This will only remove one if there are multiple
                # But why would anyone include multiple
                cell.remove(special.NO_NUMBER)
                count = False

        number = next(counter) if count else None

        row.insert(0, _equation_number(number))


def align(glyph, tokens, i):
    table, i = _equation(glyph, tokens, i)
    return [table], i


def inline(glyph, tokens, i):
    node, j = blocks(glyph, tokens, i)
    return node, j


class MathParser:
    _counter =  count(1)

    def __init__(self, glyph, **options):
        self.glyph = glyph
        self.options = options

    def _attrib(self, display):
        # area = self.area
        attrib = {"display": display}

        class_ = f"math math--{display}"
        # if area:
        #     class_ += " ".join(f" marea--{a}" for a in area)
        attrib["class"] = class_

        if display == "block":
            attrib["displaystyle"] = "true"

        return attrib

    def _parse(self, tokens, root, parser):
        nodes, i = parser(self.glyph, tokens, 0)
        root.extend(nodes)

        if 0 == len(nodes):
            nodes.append(mml.merror([mml.mtext("EMPTY EXPRESSION")]))
        elif i < len(tokens):
            nodes.append(mml.merror([mml.mtext("PARSER ERROR")]))

        return root

    def _aligned(self, tokens):
        if self.options.get("infer", False):
            return any(t.string in {r";", r"\\"} for t in tokens)
        else:
            return self.options.get("align", False)

    def parse(self, tokens, root=None):
        aligned = self._aligned(tokens)
        display = self.options.get("display", "block" if aligned else "inline")
        counter = self.options.get("counter")
        parser = align if (display == "block") else inline

        if root is None:
            root = mml.math()

        if isinstance(counter, int) and not isinstance(counter, bool):
            # reset counter
            self._counter = count(int(counter))

        root = self._parse(tokens, root, parser)

        if counter:
            enumeration(root[0], self._counter)

        root.attrib.update(self._attrib(display))

        return ET.ElementTree(root)
