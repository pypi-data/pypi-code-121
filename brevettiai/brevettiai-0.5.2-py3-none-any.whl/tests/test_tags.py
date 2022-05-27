import unittest
from brevettiai.platform.models import Tag


class TestTags(unittest.TestCase):
    tag1 = Tag(id="1", name="tag1")
    tag2 = Tag(id="2", name="tag2")
    tag3 = Tag(id="3", name="tag3", parent_id="1", created="42")
    tag1.children.append(tag3)
    tag4 = Tag(id="4", name="tag4", parent_id="2")
    tag2.children.append(tag4)
    tag5 = Tag(id="5", name="tag5", parent_id="4", created="42")
    tag4.children.append(tag5)
    tree = [tag1, tag2]

    def test_find_path(self):
        path = next(Tag.find_path(TestTags.tree, "id", "1"))
        assert all(a == b for a, b in zip(path, [TestTags.tag1, ]))

        path = next(Tag.find_path(TestTags.tree, "id", "5"))
        assert all(a == b for a, b in zip(path, [TestTags.tag2, TestTags.tag4, TestTags.tag5]))

    def test_find_named_tag(self):
        tag = next(Tag.find(TestTags.tree, "name", "tag1"))
        assert tag == TestTags.tag1

        tag = next(Tag.find(TestTags.tree, "name", "tag3"))
        assert tag == TestTags.tag3

        tags = list(Tag.find(TestTags.tree, "created", "42"))
        assert all(a == b for a, b in zip(tags, [TestTags.tag3, TestTags.tag5]))


if __name__ == '__main__':
    unittest.main()
