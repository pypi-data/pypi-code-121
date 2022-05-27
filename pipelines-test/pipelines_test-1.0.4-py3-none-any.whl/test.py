from unittest import TestCase
from hello_world import HelloWorld


class TestHelloWorld(TestCase):
    """Test class for Hello World module"""

    def test_hello_world(self):
        """Test case for hello world function"""

        print("This is test for hello world")
        hw = HelloWorld()
        self.assertEqual(hw.hello_world(), "Hello World")
        print("test")
