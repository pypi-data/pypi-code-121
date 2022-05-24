import unittest
from slpkg.binary.search import search_pkg
from slpkg.sbo.search import sbo_search_pkg


class TestFindPkg(unittest.TestCase):

    def test_search(self):
        """Testing found the name from binaries repos
        """
        name = "vlc"
        repo = "alien"
        test = search_pkg(name, repo)
        self.assertEqual(name, test)

    def test_sbo_search(self):
        """Testing found the name from binaries repos
        """
        name = "slpkg"
        test = sbo_search_pkg(name).split("/")[-2]
        self.assertEqual(name, test)


if __name__ == "__main__":
    unittest.main()
