import unittest
from slpkg.splitting import split_package
from slpkg.pkg.find import searching


class TestSplitting(unittest.TestCase):

    def test_split_pkg(self):
        path = '/var/log/packages/'
        pkg_1 = ''.join(list(searching('slpkg', path)))
        pkg_2 = ''.join(list(searching('akonadi-mime', path)))
        pkg_3 = ''.join(list(searching('autoconf-archive', path)))
        pkg_4 = ''.join(list(searching('bind', path)))

        self.assertListEqual(['slpkg', '3.9.6', 'x86_64', '1'],
                             split_package(pkg_1))
        self.assertListEqual(['akonadi-mime', '21.12.1', 'x86_64', '1'],
                             split_package(pkg_2))
        self.assertListEqual(['autoconf-archive', '2021.02.19', 'noarch', '1'],
                             split_package(pkg_3))
        self.assertListEqual(['bind', '9.16.27', 'x86_64', '1'],
                             split_package(pkg_4))


if __name__ == "__main__":
    unittest.main()
