from typing import Dict, List

SearchIndex = Dict[str, Dict[str, Dict[str, List[int]]]]
"""A dictionary of search query matches.

The search query works by splitting the provided query into words and then processing the first 20.
The first layer of the response shows each of the words that were searched for in the database.
For example, if I searched for ``hello world``, the outermost keys would be ``hello`` and ``world``.

The sub-dictionary of each of the outermost keys shows the results for each of the words.
It will show all words that matched the given word, and these are all capitalized.
For example, if I searched for ``world``, the second dictionary would have ``WORLD``, ``WORLDWIDE``, etc.

The innermost dictionary shows the chapters that contained each of the words.
Finally, the list that is the value of the innermost dictionary shows the pages in the chapter
that matched the given word.
"""
