import demoji
import typing


class Demoji:
	def remove_emojis(self, content: str, separator: str = ' ') -> str:
		return typing.cast(str, demoji.replace_with_desc(content, separator))
