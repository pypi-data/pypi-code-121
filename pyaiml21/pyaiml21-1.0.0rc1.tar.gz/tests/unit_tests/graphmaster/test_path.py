from pyaiml21.graphmaster import GraphMaster
from pyaiml21.botconfig import BotConfig
from pyaiml21.ast import Node, Category
from pyaiml21.stdlib import PATTERNS as STD_PATTERNS


def test_simple_path():
    gm = GraphMaster(BotConfig(), "keep_first")
    gm._known_patterns = STD_PATTERNS
    category = Category(
        pattern=Node.Element("pattern", children=[Node.Value("hello")]),
        that=Node.Element("that", children=[Node.Value("that")]),
        topic=Node.Element("topic", children=[Node.Value("topic")]),
        template=Node.Element("template")
    )
    gm.save(category)
    res = gm.match("HELLO", "THAT", "TOPIC")  # matching already preprocessed nodes
    assert res
    assert res[0] == category.template
