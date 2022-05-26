from random import choice

ignorable_function_names = ['run', 'main', 'test', 'f', 't']

f = lambda function_name: function_name in ignorable_function_names

t = lambda: all([f(choice(ignorable_function_names)), not f('foo')])
