from math import ceil, floor

operator_cases_happy = {
    'column + column': (
        lambda x, y: x + x,
        lambda x, y: f"{x.get_sql()} + {x.get_sql()}"
    ),
    'column + literal': (
        lambda x, y: x + 3.0,
        lambda x, y: f"{x.get_sql()} + 3.0"
    ),
    'literal + column': (
        lambda x, y: 2.0 + x,
        lambda x, y: f"2.0 + {x.get_sql()}"
    ),
    'column - column': (
        lambda x, y: x - x,
        lambda x, y: f"{x.get_sql()} - {x.get_sql()}"
    ),
    'column - literal': (
        lambda x, y: x - 3.0,
        lambda x, y: f"{x.get_sql()} - 3.0"
    ),
    'literal - column': (
        lambda x, y: 2.0 - x,
        lambda x, y: f"2.0 - {x.get_sql()}"
    ),
    'column * column': (
        lambda x, y: x * x,
        lambda x, y: f"{x.get_sql()} * {x.get_sql()}"
    ),
    'column * literal': (
        lambda x, y: x * 3.0,
        lambda x, y: f"{x.get_sql()} * 3.0"
    ),
    'literal * column': (
        lambda x, y: 2.0 * x,
        lambda x, y: f"2.0 * {x.get_sql()}"
    ),
    'column // column': (
        lambda x, y: x // x,
        lambda x, y: f"{x.get_sql()} / {x.get_sql()}"
    ),
    'column // literal': (
        lambda x, y: x // 3.0,
        lambda x, y: f"{x.get_sql()} / 3.0"
    ),
    'literal // column': (
        lambda x, y: 2.0 // x,
        lambda x, y: f"2.0 / {x.get_sql()}"
    ),
    'column / column': (
        lambda x, y: x / x,
        lambda x, y: f"{x.get_sql()} / (cast({x.get_sql()} AS DOUBLE))"
    ),
    'column / literal': (
        lambda x, y: x / 3.0,
        lambda x, y: f"{x.get_sql()} / (cast(3.0 AS DOUBLE))"
    ),
    'literal / column': (
        lambda x, y: 2.0 / x,
        lambda x, y: f"2.0 / (cast({x.get_sql()} AS DOUBLE))"
    ),
    'column % column': (
        lambda x, y: x % x,
        lambda x, y: f"{x.get_sql()} % {x.get_sql()}"
    ),
    'column % literal': (
        lambda x, y: x % 3.0,
        lambda x, y: f"{x.get_sql()} % 3.0"
    ),
    'literal % column': (
        lambda x, y: 2.0 % x,
        lambda x, y: f"2.0 % {x.get_sql()}"
    ),
    'column & column': (
        lambda x, y: (x > 100) & (x < 200),
        lambda x, y: f"({(x > 100).get_sql()}) AND ({(x < 200).get_sql()})"
    ),
    'column | column': (
        lambda x, y: (x > 100) | (x < 200),
        lambda x, y: f"({(x > 100).get_sql()}) OR ({(x < 200).get_sql()})"
    ),
    '~column': (
        lambda x, y: ~(x == 2),
        lambda x, y: f"NOT ({(x == 2).get_sql()})",
    ),
    'column == column': (
        lambda x, y: x == x,
        lambda x, y: f"{x.get_sql()} = {x.get_sql()}"
    ),
    'column == literal': (
        lambda x, y: x == 2,
        lambda x, y: f"{x.get_sql()} = 2"
    ),
    'literal == column': (
        lambda x, y: 2 == x,
        lambda x, y: f"{x.get_sql()} = 2"
    ),
    'column != column': (
        lambda x, y: x != x,
        lambda x, y: f"{x.get_sql()} != {x.get_sql()}"
    ),
    'column != literal': (
        lambda x, y: x != 2,
        lambda x, y: f"{x.get_sql()} != 2"
    ),
    'literal != column': (
        lambda x, y: 2 != x,
        lambda x, y: f"{x.get_sql()} != 2"
    ),
    'column > column': (
        lambda x, y: x > x,
        lambda x, y: f"{x.get_sql()} > {x.get_sql()}"
    ),
    'column > literal': (
        lambda x, y: x > 2,
        lambda x, y: f"{x.get_sql()} > 2"
    ),
    'literal > column': (
        lambda x, y: 2 > x,
        lambda x, y: f"{x.get_sql()} < 2"
    ),
    'column < column': (
        lambda x, y: x < x,
        lambda x, y: f"{x.get_sql()} < {x.get_sql()}"
    ),
    'column < literal': (
        lambda x, y: x < 2,
        lambda x, y: f"{x.get_sql()} < 2"
    ),
    'literal < column': (
        lambda x, y: 2 < x,
        lambda x, y: f"{x.get_sql()} > 2"
    ),
    '-column': (
        lambda x, y: -x,
        lambda x, y: f"-{x.get_sql()}"
    ),
    'column <= column': (
        lambda x, y: x <= x,
        lambda x, y: f"{x.get_sql()} <= {x.get_sql()}"
    ),
    'column <= literal': (
        lambda x, y: x <= 2,
        lambda x, y: f"{x.get_sql()} <= 2"
    ),
    'literal <= column': (
        lambda x, y: 2 <= x,
        lambda x, y: f"{x.get_sql()} >= 2"
    ),
    'column >= column': (
        lambda x, y: x >= x,
        lambda x, y: f"{x.get_sql()} >= {x.get_sql()}"
    ),
    'column >= literal': (
        lambda x, y: x >= 2,
        lambda x, y: f"{x.get_sql()} >= 2"
    ),
    'literal >= column': (
        lambda x, y: 2 >= x,
        lambda x, y: f"{x.get_sql()} <= 2"
    ),
    'column ** column': (
        lambda x, y: x ** x,
        lambda x, y: f"power({x.get_sql()}, {x.get_sql()})"
    ),
    'column ** literal': (
        lambda x, y: x ** 2,
        lambda x, y: f"power({x.get_sql()}, 2)"
    ),
    'literal ** column': (
        lambda x, y: 2 ** x,
        lambda x, y: f"power(2, {x.get_sql()})"
    ),
    'ceil(column)': (
        lambda x, y: ceil(x),
        lambda x, y: f"ceil({x.get_sql()})"
    ),
    'floor(column)': (
        lambda x, y: floor(x),
        lambda x, y: f"floor({x.get_sql()})"
    ),
    'abs(column)': (
        lambda x, y: abs(x),
        lambda x, y: f"abs({x.get_sql()})"
    ),
    'round(column)': (
        lambda x, y: round(x),
        lambda x, y: f"round({x.get_sql()}, 0)"
    ),
    'round(column, 2)': (
        lambda x, y: round(x, 2),
        lambda x, y: f"round({x.get_sql()}, 2)"
    ),
}

