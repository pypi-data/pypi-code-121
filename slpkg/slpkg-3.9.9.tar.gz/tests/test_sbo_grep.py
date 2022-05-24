import unittest
from slpkg.sbo.greps import SBoGrep


class TestSBoGreps(unittest.TestCase):

    def setUp(self):
        self.grep = SBoGrep('Flask')

    def test_source(self):
        """Test package source
        """
        source = self.grep.source()
        flask_source = ('https://files.pythonhosted.org/packages/4e/0b/'
                        'cb02268c90e67545a0e3a37ea1ca3d45de3aca43ceb7dbf'
                        '1712fb5127d5d/Flask-1.1.2.tar.gz')
        self.assertEqual(source, flask_source)

    def test_requires(self):
        """Test package requires
        """
        requires = self.grep.requires()
        flask_dep = ['werkzeug', 'python3-itsdangerous', 'click']
        self.assertListEqual(requires, flask_dep)

    def test_version(self):
        """Test package version
        """
        version = self.grep.version()
        flask_ver = '1.1.2'
        self.assertEqual(version, flask_ver)

    def test_checksum(self):
        """Test package checksum
        """
        checksum = self.grep.checksum()
        flask_md5 = ['0da4145d172993cd28a6c619630cc19c']
        self.assertListEqual(checksum, flask_md5)

    def test_description(self):
        """Test package description
        """
        desc = self.grep.description()
        flask_desc = 'Flask (Microframework for Python)'
        self.assertEqual(desc, flask_desc)


if __name__ == "__main__":
    unittest.main()
