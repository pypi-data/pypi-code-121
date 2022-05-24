from datetime import datetime
import re

def _get_date(string):
	return datetime.strptime(string, '%Y-%m-%d').date()
_converters = dict(
	int=(int, r'-?\d+'),
	str=(str, r'[^/]+'),
	date=(_get_date, r'\d\d\d\d-\d\d-\d\d'),
)

class Pattern:
	'''
	Note - users are never likely to use Pattern directly.
	They need to know how it works, though, because it's used by Router.

	TODO - document better.

	Provides pattern matching for sub paths.
	Examples:
	foo/
	<int:author_id>/
	authors-<int:author_id>/
	foos/<int:foo_id>/
	<str:segment>/
	<date:open_date>/
	authors/<int:author_id>/<date:publish_date>/
	'''
	def __init__(self, pattern):
		if not pattern.endswith('/') :
			raise ValueError(f'Invalid Pattern: "{pattern}". Must end with "/" ')

		regex = ''
		types = []
		for index, part in enumerate(re.split(r'<(\w+:?\w*)>', pattern)) :
			if index % 2 == 0 :
				regex += re.escape(part)
			else :
				try :
					converter, converter_name = part.split(':')
				except ValueError :
					raise ValueError(f'Invalid caturing param: <{part}>. Must use <type:name> syntax.')
				if not converter_name :
					raise ValueError(f'Invalid caturing param: <{part}>. Name must not be empty.')
				try :
					converter, converter_regex = _converters[converter]
				except KeyError :
					raise ValueError(f'Invalid converter "{converter}" in pattern "{pattern}"')

				regex += f'(?P<{converter_name}>{converter_regex})'
				types.append((converter_name, converter))

		self._regex = regex
		self._types = types

	def match(self, path) -> tuple :
		'''
		If we match path, return the prefix that we match, and a dict of captures.

		Otherwise, raise ValueError
		'''
		match = re.match(self._regex, path)
		if not match :
			raise ValueError()

		return (
			match.group(0),
			# Note - may raise ValueError
			{
				name: converter(match.group(name))
				for name, converter in self._types
			}
		)
