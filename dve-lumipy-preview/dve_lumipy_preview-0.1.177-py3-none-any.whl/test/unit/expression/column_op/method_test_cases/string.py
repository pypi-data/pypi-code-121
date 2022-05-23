
str_method_cases_happy = {
    'column.str_len': (
        lambda x, y: x.cast(str).str.len(),
        lambda x, y: f"length({x.cast(str).get_sql()})"
    ),
    'column.str.trim()': (
        lambda x, y: x.cast(str).str.trim(),
        lambda x, y: f"trim({x.cast(str).get_sql()})"
    ),
    'column.str.trim("", left)': (
        lambda x, y: x.cast(str).str.trim(trim_type='left'),
        lambda x, y: f"ltrim({x.cast(str).get_sql()})"
    ),
    'column.str.trim("", right)': (
        lambda x, y: x.cast(str).str.trim(trim_type='right'),
        lambda x, y: f"rtrim({x.cast(str).get_sql()})"
    ),
    'column.str.trim("stuff")': (
        lambda x, y: x.cast(str).str.trim('stuff'),
        lambda x, y: f"trim({x.cast(str).get_sql()}, 'stuff')"
    ),
    'column.str.trim("stuff", left)': (
        lambda x, y: x.cast(str).str.trim('stuff', trim_type='left'),
        lambda x, y: f"ltrim({x.cast(str).get_sql()}, 'stuff')"
    ),
    'column.str.trim("stuff", right)': (
        lambda x, y: x.cast(str).str.trim('stuff', trim_type='right'),
        lambda x, y: f"rtrim({x.cast(str).get_sql()}, 'stuff')"
    ),
    'column.str.like': (
        lambda x, y: x.cast(str).str.like('%str%'),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE '%str%'"
    ),
    'column.str.not_like': (
        lambda x, y: x.cast(str).str.not_like('%str%'),
        lambda x, y: f"({x.cast(str).get_sql()}) NOT LIKE '%str%'"
    ),
    'column.str.glob': (
        lambda x, y: x.cast(str).str.glob('*str*'),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB '*str*'"
    ),
    'column.str.not_glob': (
        lambda x, y: x.cast(str).str.not_glob('*str*'),
        lambda x, y: f"({x.cast(str).get_sql()}) NOT GLOB '*str*'"
    ),
    'column.str.regexp': (
        lambda x, y: x.cast(str).str.regexp('^.*?$'),
        lambda x, y: f"({x.cast(str).get_sql()}) REGEXP '^.*?$'"
    ),
    'column.str.not_regexp': (
        lambda x, y: x.cast(str).str.not_regexp('^.*?$'),
        lambda x, y: f"({x.cast(str).get_sql()}) NOT REGEXP '^.*?$'"
    ),
    'column.str.concat': (
        lambda x, y: x.cast(str).str.concat(y.cast(str)),
        lambda x, y: f"({x.cast(str).get_sql()}) || ({y.cast(str).get_sql()})"
    ),
    'column.str.replace': (
        lambda x, y: x.cast(str).str.replace('a', 'b'),
        lambda x, y: f"Replace({x.cast(str).get_sql()}, 'a', 'b')"
    ),
    'column.str.lower': (
        lambda x, y: x.cast(str).str.lower(),
        lambda x, y: f"Lower({x.cast(str).get_sql()})"
    ),
    'column.str.upper': (
        lambda x, y: x.cast(str).str.upper(),
        lambda x, y: f"Upper({x.cast(str).get_sql()})"
    ),
    'column.str.soundex': (
        lambda x, y: x.cast(str).str.soundex(),
        lambda x, y: f"soundex({x.cast(str).get_sql()})"
    ),
    'column.str.substr()': (
        lambda x, y: x.cast(str).str.substr(1),
        lambda x, y: f"substr({x.cast(str).get_sql()}, 1, 1)"
    ),
    'column.str.substr(1, 3)': (
        lambda x, y: x.cast(str).str.substr(1, 3),
        lambda x, y: f"substr({x.cast(str).get_sql()}, 1, 3)"
    ),
    'column.str.unicode': (
        lambda x, y: x.cast(str).str.unicode(),
        lambda x, y: f"unicode({x.cast(str).get_sql()})"
    ),
    'column.str.replicate': (
        lambda x, y: x.cast(str).str.replicate(2),
        lambda x, y: f"replicate({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.reverse': (
        lambda x, y: x.cast(str).str.reverse(),
        lambda x, y: f"reverse({x.cast(str).get_sql()})"
    ),
    'column.str.left_str': (
        lambda x, y: x.cast(str).str.left_str(2),
        lambda x, y: f"leftstr({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.right_str': (
        lambda x, y: x.cast(str).str.right_str(2),
        lambda x, y: f"rightstr({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.pad_str(2, right)': (
        lambda x, y: x.cast(str).str.pad(2, 'right'),
        lambda x, y: f"padr({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.pad_str(2, center)': (
        lambda x, y: x.cast(str).str.pad(2, 'center'),
        lambda x, y: f"padc({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.pad_str(2, left)': (
        lambda x, y: x.cast(str).str.pad(2, 'left'),
        lambda x, y: f"padl({x.cast(str).get_sql()}, 2)"
    ),
    'column.str.str_filter': (
        lambda x, y: x.cast(str).str.filter('test'),
        lambda x, y: f"strfilter({x.cast(str).get_sql()}, 'test')"
    ),
    'column.str.index(abc, 3)': (
        lambda x, y: x.cast(str).str.index('abc', 3),
        lambda x, y: f"charindex('abc', {x.cast(str).get_sql()}, 3)"
    ),
    'column.str.proper': (
        lambda x, y: x.cast(str).str.proper(),
        lambda x, y: f"proper({x.cast(str).get_sql()})"
    ),
    'column.str.contains(literal, True)': (
        lambda x, y: x.cast(str).str.contains('test', case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB '*test*'"
    ),
    'column.str.contains(expr, True)': (
        lambda x, y: x.cast(str).str.contains(y.cast(str), case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB ('*' || (({y.cast(str).get_sql()}) || '*'))"
    ),
    'column.str.contains(literal, False)': (
        lambda x, y: x.cast(str).str.contains('test', case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE '%test%'"
    ),
    'column.str.contains(expr, False)': (
        lambda x, y: x.cast(str).str.contains(y.cast(str), case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE ('%' || (({y.cast(str).get_sql()}) || '%'))"
    ),
    'column.str.startswith(literal, True)': (
        lambda x, y: x.cast(str).str.startswith('test', case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB 'test*'"
    ),
    'column.str.startswith(expr, True)': (
        lambda x, y: x.cast(str).str.startswith(y.cast(str), case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB (({y.cast(str).get_sql()}) || '*')"
    ),
    'column.str.startswith(literal, False)': (
        lambda x, y: x.cast(str).str.startswith('test', case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE 'test%'"
    ),
    'column.str.startswith(expr, False)': (
        lambda x, y: x.cast(str).str.startswith(y.cast(str), case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE (({y.cast(str).get_sql()}) || '%')"
    ),
    'column.str.endswith(literal, True)': (
        lambda x, y: x.cast(str).str.endswith('test', case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB '*test'"
    ),
    'column.str.endswith(expr, True)': (
        lambda x, y: x.cast(str).str.endswith(y.cast(str), case_sensitive=True),
        lambda x, y: f"({x.cast(str).get_sql()}) GLOB ('*' || ({y.cast(str).get_sql()}))"
    ),
    'column.str.endswith(literal, False)': (
        lambda x, y: x.cast(str).str.endswith('test', case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE '%test'"
    ),
    'column.str.endswith(expr, False)': (
        lambda x, y: x.cast(str).str.endswith(y.cast(str), case_sensitive=False),
        lambda x, y: f"({x.cast(str).get_sql()}) LIKE ('%' || ({y.cast(str).get_sql()}))"
    ),
    'column.str.to_date()': (
        lambda x, y: y.cast(str).str.to_date(),
        lambda x, y: f"To_Date({y.cast(str).get_sql()})"
    ),
}

str_method_cases_unhappy = {
    'column.str.trim("", invalid)': (
        lambda x, y: x.cast(str).str.trim(trim_type='nonsense'),
        ValueError,
        lambda x, y: "Invalid trim type 'nonsense'. Must be one of 'right', 'left' or 'both'. Defaults to 'both'."
    ),
    'column.str.pad(2, invalid)': (
        lambda x, y: x.cast(str).str.pad(2, 'nonsense'),
        ValueError,
        lambda x, y: "Unrecognised pad type: nonsense",
    ),
    'column.str.sub_str(bad index)': (
        lambda x, y: x.cast(str).str.substr(0),
        ValueError,
        lambda x, y: "Invalid input for start_ind: 0. SQL substring index must be a positive non-zero int (indexing from string start) or negative (indexing backward from string end)."
    ),
}