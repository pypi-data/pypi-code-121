from unittest import TestCase

from traxer.client import connect

class TestFolders(TestCase):

    def setUp(self):
        self.sess = connect("http://localhost:5000")
        self.folder = "unittest_rg56b46rg6rtb6554"

    def test_new_folder(self):
        pass

    def test_get_folder(self):
        pass

    def test_folder_exists(self):
        pass

    def test_new_existing_folder(self):
        pass
    
    def test_remove_folder(self):
        pass