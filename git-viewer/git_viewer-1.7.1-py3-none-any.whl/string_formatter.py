#!/usr/bin/env python3

import string


class MyFormatter(string.Formatter):

	"""
	This Formatter extends the default format specification by an optional prefix.
	https://docs.python.org/3.4/library/string.html#format-string-syntax
	https://docs.python.org/3.4/library/string.html#format-specification-mini-language

	This prefix can be either one of:
	- l: The first character of the inserted string will be converted to lower case.
	- u: The first character of the inserted string will be converted to upper case.
	"""

	def format_field(self, value, format_spec):
		if not format_spec:
			return super().format_field(value, format_spec)

		if format_spec[0] == 'l':
			format_spec = format_spec[1:]
			if value:
				value = value[0].lower() + value[1:]
		elif format_spec[0] == 'u':
			format_spec = format_spec[1:]
			if value:
				value = value[0].upper() + value[1:]

		return super().format_field(value, format_spec)


formatter = MyFormatter()


if __name__ == '__main__':
	test = "test"
	print(formatter.format("test = {}", test))
	print(formatter.format("{:u} 123.", test))
	print(formatter.format("This is a {:l}.", test))
	print("")

	test = "Test"
	print(formatter.format("test = {}", test))
	print(formatter.format("{:u} 123.", test))
	print(formatter.format("This is a {:l}.", test))
