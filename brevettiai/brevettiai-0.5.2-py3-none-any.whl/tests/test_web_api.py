import unittest
from brevettiai.platform import BrevettiAI


@unittest.skip("Temporarily disabled")
class TestPlatformJob(unittest.TestCase):
    def test_platform_login(self):
        web = BrevettiAI()
        assert(len(web.user) > 0)  # Dict is not empty

    def test_application_classes(self):
        web = BrevettiAI()
        application = web.get_application("9b551660-7f4d-4714-aabf-9c704d58afa6")
        assert(application.type == 1)


if __name__ == '__main__':
    unittest.main()
