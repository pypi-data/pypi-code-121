from jft.string.format import f as format_one
f = lambda λ, fn=format_one: [fn(π) for π in λ]
t = lambda: list('abc') == f(list('abc'), lambda x: x)