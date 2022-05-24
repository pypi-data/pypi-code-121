import unittest
from pypers.utils import xmldom
import shutil
import os


class Test(unittest.TestCase):

    def setUp(self):
        self.path = 'toto/'
        try:
            shutil.rmtree(self.path)
        except Exception as e:
            pass
        os.mkdir(self.path)
        self.original_file = os.path.join(self.path, 'test.xml')
        self.original_xsl = os.path.join(self.path, 'test.xsl')

        shutil.copy(os.path.join(os.path.dirname(__file__), 'files',
                                 'test.xml'),
                    self.original_file)
        shutil.copy(os.path.join(os.path.dirname(__file__), 'files',
                                 'test.xsl'),
                    self.original_xsl)

    def tearDown(self):
        try:
            shutil.rmtree(self.path)
        except Exception as e:
            pass

    def test_remove_doctype(self):
        f = xmldom.remove_doctype(self.original_file)
        self.assertEqual(f, self.original_file)
        with open(f) as reader:
            line = reader.readlines()[0]
            self.assertTrue('<!DOCTYPE document SYSTEM' not in line)

    def test_clean_xmlfile(self):
        ordinals = ((221, '['), (170, ']'), (249, '&#233;'))
        chars = (('a', 'b'), ('A', 'B'))
        f = xmldom.clean_xmlfile(self.original_file,
                                 ordinals=ordinals, chars=chars)
        with open(f) as reader:
            lines = reader.readlines()
            # Test special chars removal
            self.assertTrue(len(lines) == 85)
            lines = ' '.join([line.replace('\n', '') for line in lines])
            # Test ordinals
            self.assertTrue('[xmlns="http://www.wipo.int/stbndbrds'
                            '/XMLSchemb/trbdembrks"[' in lines)
            # Test chars replacement
            self.assertTrue('a' not in lines)
            self.assertTrue('A' not in lines)

        f = xmldom.clean_xmlfile(self.original_file,
                                 ordinals=ordinals, chars=chars)
        self.assertEqual(f, '%s.clean' % self.original_file)
        os.remove(f)
        f = xmldom.clean_xmlfile(self.original_file, overwrite=True,
                                 ordinals=ordinals, chars=chars)
        self.assertEqual(f, self.original_file)
        with open(os.path.join(self.path, 'empty.xml'), 'w') as f:
            pass
        try:
            f = xmldom.clean_xmlfile(os.path.join(self.path, 'empty.xml'))
            self.fail("Should raise error on empty")
        except Exception as f:
            pass


    def test_get_nodevalue(self):
        xmldom.remove_doctype(self.original_file)
        # Still some errors in xml
        try:
            v = xmldom.get_nodevalue('ApplicationNumber',
                                     file=self.original_file)
        except Exception as e:
            pass
        xmldom.clean_xmlfile(self.original_file, overwrite=True,
                             ordinals=((221, ''),))
        v = xmldom.get_nodevalue('ApplicationNumber', file=self.original_file)
        self.assertEqual(v, '4199837560')
        v = xmldom.get_nodevalue('Totot', file=self.original_file)
        self.assertEqual(v, '')
        try:
            v = xmldom.get_nodevalue('toto')
            self.fail("Should not arrive here")
        except Exception as e:
            pass

    def test_set_nodevalue(self):
        try:
            v = xmldom.get_nodevalue('toto')
            self.fail("Should not arrive here")
        except Exception as e:
            pass
        xmldom.remove_doctype(self.original_file)
        # Still some errors in xml
        v = xmldom.set_nodevalue('toto', '1',
                                 file=self.original_file)
        self.assertEqual(v, None)
        xmldom.clean_xmlfile(self.original_file, overwrite=True,
                             ordinals=((221, ''),))
        s = xmldom.set_nodevalue('ApplicationNumber', '4',
                                 file=self.original_file)
        self.assertEqual(s, self.original_file)
        v = xmldom.get_nodevalue('ApplicationNumber', file=self.original_file)
        self.assertEqual(v, '4')
        s = xmldom.set_nodevalue('InexistingValue', '4',
                                 file=self.original_file)
        v = xmldom.get_nodevalue('InexistingValue', file=self.original_file)
        self.assertEqual(v, '')
        s = xmldom.set_nodevalue('InexistingValue', '4', force=True,
                                 file=self.original_file)
        v = xmldom.get_nodevalue('InexistingValue', file=self.original_file)
        self.assertEqual(v, '4')

    def test_get_nodevalues(self):
        xmldom.remove_doctype(self.original_file)
        # Still some errors in xml
        try:
            v = xmldom.get_nodevalues('ApplicationNumber',
                                      file=self.original_file)
            self.fail("Should not arrive here")
        except Exception as e:
            pass
        xmldom.clean_xmlfile(self.original_file, overwrite=True,
                             ordinals=((221, ''),))
        v = xmldom.get_nodevalues('ApplicationNumber', file=self.original_file)
        self.assertEqual(v, ['4199837560'])
        v = xmldom.get_nodevalues('Totot', file=self.original_file)
        self.assertEqual(v, [])
        try:
            v = xmldom.get_nodevalues('toto')
            self.fail("Should not arrive here")
        except Exception as e:
            pass

    def test_transform(self):
        xmldom.remove_doctype(self.original_file)
        xmldom.clean_xmlfile(self.original_file, overwrite=True,
                             ordinals=((221, ''),))
        transformed = os.path.join(self.path, 'transformed.xml')
        xmldom.transform(self.original_file, self.original_xsl, transformed)
        with open(transformed, 'r') as f:
            lines = f.readlines()
        self.assertTrue(len(lines) > 1)

    def test_create_element(self):
        xmldom.remove_doctype(self.original_file)
        xmldom.clean_xmlfile(self.original_file, overwrite=True,
                             ordinals=((221, ''),))
        xmldom.create_element(self.original_file, 'toto', '4')
        v = xmldom.get_nodevalue('toto', file=self.original_file)
        self.assertEqual(v, '4')


if __name__ == "__main__":
    unittest.main()
