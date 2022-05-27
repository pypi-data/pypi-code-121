def format_long_list(value, prefix=None, max_items=None):
	ret = ''
	if prefix != None:
		ret = prefix

	leftover = 0
	if len(value) > max_items:
		leftover = len(value) - max_items
		value = value[:max_items]

	ret += ', '.join(value)
	if leftover > 0:
		ret += f' ...and {leftover} more'

	return ret
