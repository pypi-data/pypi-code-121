from unittest import TestCase
import os
import shutil
from virtualenv_update_path import update_path_in_bat_file, update_path_in_base_file


class BatFileUpdateTests(TestCase):

    def setUp(self) -> None:
        self.env_dir = os.path.dirname(__file__) + '/data/env'
        self.path_dir = os.path.dirname(__file__) + '/data/path/to/add'
        os.makedirs(self.env_dir, exist_ok=True)
        os.makedirs(self.path_dir, exist_ok=True)
        return super().setUp()
    
    def tearDown(self) -> None:
        if os.path.exists(os.path.dirname(__file__) + '/data'):
            shutil.rmtree(os.path.dirname(__file__) + '/data')
        return super().tearDown()
    
    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            update_path_in_bat_file(os.path.join(self.env_dir, 'activate.bat'), self.path_dir)

    def test_missing_path_raises(self):
        with self.assertRaises(FileNotFoundError):
            update_path_in_bat_file(os.path.join(self.env_dir, 'activate.bat'), self.path_dir+'2')

    def test_added_to_empty_file(self):
        filename = os.path.join(self.env_dir, 'activate.bat')
        with open(filename, 'w') as f:
            pass

        update_path_in_bat_file(filename, self.path_dir)

        with open(filename, 'r') as f:
            data = f.read()
        
        self.assertEqual(f'\nset "PATH={self.path_dir};%PATH%"\n', data)

    def test_added_to_existing_file(self):
        filename = os.path.join(self.env_dir, 'activate.bat')
        with open(filename, 'w') as f:
            f.write('ABCD\n')

        update_path_in_bat_file(filename, self.path_dir)

        with open(filename, 'r') as f:
            data = f.read()
        
        self.assertEqual(f'ABCD\n\nset "PATH={self.path_dir};%PATH%"\n', data)


class BaseFileUpdateTests(TestCase):

    def setUp(self) -> None:
        self.env_dir = os.path.dirname(__file__) + '/data/env'
        self.path_dir = os.path.dirname(__file__) + '/data/path/to/add'
        os.makedirs(self.env_dir, exist_ok=True)
        os.makedirs(self.path_dir, exist_ok=True)
        return super().setUp()
    
    def tearDown(self) -> None:
        if os.path.exists(os.path.dirname(__file__) + '/data'):
            shutil.rmtree(os.path.dirname(__file__) + '/data')
        return super().tearDown()
    
    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            update_path_in_base_file(os.path.join(self.env_dir, 'activate.bat'), self.path_dir)

    def test_missing_path_raises(self):
        with self.assertRaises(FileNotFoundError):
            update_path_in_base_file(os.path.join(self.env_dir, 'activate.bat'), self.path_dir+'2')

    def test_added_to_empty_file(self):
        filename = os.path.join(self.env_dir, 'activate.bat')
        with open(filename, 'w') as f:
            pass

        update_path_in_base_file(filename, self.path_dir)

        with open(filename, 'r') as f:
            data = f.read()
        desired_contents = '\nPATH="' + self.path_dir.replace('\\', '/') + ';$PATH"\nexport PATH\nhash -r 2>/dev/null\n'
        self.assertEqual(desired_contents, data)

    def test_added_to_existing_file(self):
        filename = os.path.join(self.env_dir, 'activate.bat')
        with open(filename, 'w') as f:
            f.write('ABCD\n')

        update_path_in_base_file(filename, self.path_dir)

        with open(filename, 'r') as f:
            data = f.read()
        
        desired_contents = 'ABCD\n\nPATH="' + self.path_dir.replace('\\', '/') + ';$PATH"\nexport PATH\nhash -r 2>/dev/null\n'
        self.assertEqual(desired_contents, data)
