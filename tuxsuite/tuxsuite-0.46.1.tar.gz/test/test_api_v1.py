# -*- coding: utf-8 -*-

from test.api_v1 import FakeRandom


class TestFakeRandom:
    sample_data = {
        "git_repo": "https://github.com/torvalds/linux.git",
        "git_ref": "master",
        "target_arch": "x86_64",
        "toolchain": "gcc-9",
        "kconfig": ["allyesconfig"],
    }

    def test_sha_is_based_on_input(self):
        fr1 = FakeRandom(self.sample_data)
        fr2 = FakeRandom(self.sample_data)
        assert fr1.get_git_sha() == fr2.get_git_sha()
