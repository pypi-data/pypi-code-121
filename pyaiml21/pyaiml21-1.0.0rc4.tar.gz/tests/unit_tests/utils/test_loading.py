from pyaiml21.utils import load_aiml_set, aiml_set_fromstring
from pyaiml21.utils import load_aiml_map, aiml_map_fromstring
import tempfile
from pathlib import Path


def from_file(text: str, expected: set, func):
    with tempfile.TemporaryDirectory() as td:
        file = Path(td) / "sample.set"
        with open(file, "w") as f:
            f.write(text)
        from_file = func(file)
        assert from_file == expected


TEST_CASES_SETS = [
    ("", set()),

    # alice format
    ("text", {"TEXT"}),
    ("a\na b\nab\na b   c\n c", {"A", "A B", "AB", "A B C", "C"}),

    # pandorabots format
    ('["some text"]', {"SOME TEXT"}),
    ('[["other", "text"]]', {"OTHER TEXT"}),

    ('[["a"], ["a", "b"], ["a b   c"]]', {"A", "A B", "A B C"}),
    ('["a", "a b", "a b c"]', {"A", "A B", "A B C"})
]


def test_loading_sets():
    for text, expected in TEST_CASES_SETS:
        parsed = aiml_set_fromstring(text)
        assert parsed == expected
        from_file(text, expected, load_aiml_set)


TEST_CASES_MAPS = [
    ("", dict()),

    # alice format
    ("key:value", dict(KEY="value")),
    (":value", dict()),
    ("key:value:long", dict(KEY="value:long")),
    ("k:v a l u e\na:b\n1:4", {"K": "v a l u e", "A": "b", "1": "4"}),

    # pandorabots format
    ('[["key", "value"]]', dict(KEY="value")),
    ('[["     ", "value"]]', dict()),
    ('[["key", "value long"], ["a   b", "c"], ["1", "2"]]', {
        "KEY": "value long",   "A B": "c",   "1": "2"}),
    ('[["key",\n\n"value"],\n["a","b"]]', dict(KEY="value", A="b"))
]


def test_loading_maps():
    for text, expected in TEST_CASES_MAPS:
        parsed = aiml_map_fromstring(text)
        assert parsed == expected
        from_file(text, expected, load_aiml_map)
