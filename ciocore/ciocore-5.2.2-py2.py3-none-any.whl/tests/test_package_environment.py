""" test package_env """

import unittest

from ciocore.package_environment import PackageEnvironment


class InitPlatformTest(unittest.TestCase):
    def setUp(self):
        self.env_1a = {"name": "VAR1", "value": "a", "merge_policy": "append"}

    def test_init_empty_env(self):
        p = PackageEnvironment()
        self.assertEqual(dict(p), {})

    def test_init_specified_platform_package(self):
        package = {"environment": [self.env_1a], "platform": "windows"}
        p = PackageEnvironment(package)
        self.assertEqual(p.platform, "windows")

    def test_init_package_unspecified_platform_is_linux(self):
        package = {"environment": [self.env_1a]}
        p = PackageEnvironment(package)
        self.assertEqual(p.platform, "linux")

    def test_ignore_if_try_to_specify_platform_with_arg_as_package(self):
        package = {"environment": [self.env_1a]}
        p = PackageEnvironment(package, "windows")
        self.assertEqual(p.platform, "linux")

    def test_init_specified_list(self):
        p = PackageEnvironment([self.env_1a], "windows")
        self.assertEqual(p.platform, "windows")

    def test_init_linux_list_default(self):
        p = PackageEnvironment([self.env_1a])
        self.assertEqual(p.platform, "linux")


class ExtendEnvTest(unittest.TestCase):
    def setUp(self):
        self.env_1a = {"name": "VAR1", "value": "a", "merge_policy": "append"}
        self.env_2a = {"name": "VAR2", "value": "b", "merge_policy": "append"}
        self.env_3x = {"name": "VAR3", "value": "c", "merge_policy": "exclusive"}

    def test_extend_when_empty_can_initialize_platform(self):
        p = PackageEnvironment()
        package = {"environment": [self.env_1a], "platform": "windows"}
        p.extend(package)
        self.assertEqual(p.platform, "windows")

    def test_extend_cannot_override_platform(self):
        win_package = {"environment": [self.env_1a], "platform": "windows"}
        p = PackageEnvironment(win_package)
        lin_package = {"environment": [self.env_2a], "platform": "linux"}
        with self.assertRaises(ValueError):
            p.extend(lin_package)

    def test_extend_same_platform_no_error(self):
        lin_package1 = {"environment": [self.env_1a], "platform": "linux"}
        p = PackageEnvironment(lin_package1)
        lin_package2 = {"environment": [self.env_2a], "platform": "linux"}
        p.extend(lin_package2)
        self.assertEqual(p.platform, "linux")

    def test_extend_append(self):
        p = PackageEnvironment([self.env_1a])
        package = {"environment": [{"name": "VAR1", "value": "b", "merge_policy": "append"}]}
        p.extend(package)
        self.assertEqual(p["VAR1"], "a:b")

    def test_extend_append_windows(self):
        p = PackageEnvironment([self.env_1a], "windows")
        p.extend([{"name": "VAR1", "value": "b", "merge_policy": "append"}])
        self.assertEqual(p["VAR1"], "a;b")

    def test_extend_exclusive_when_empty(self):
        p = PackageEnvironment()
        package = {"environment": [self.env_3x]}
        p.extend(package)
        self.assertEqual(p["VAR3"], "c")

    def test_extend_exclusive_overwrites(self):
        p = PackageEnvironment([self.env_3x])
        package = {"environment": [{"name": "VAR3", "value": "d", "merge_policy": "exclusive"}]}
        p.extend(package)
        self.assertEqual(p["VAR3"], "d")

    def test_fail_when_invalid_merge_policy(self):
        p = PackageEnvironment()
        package = {"environment": [{"name": "VAR1", "value": "bar", "merge_policy": "foo"}]}
        with self.assertRaises(ValueError):
            p.extend(package)

    def test_many(self):
        p = PackageEnvironment([self.env_1a])
        package = {
            "environment": [
                {"name": "VAR1", "value": "gob", "merge_policy": "append"},
                {"name": "VAR2", "value": "baz", "merge_policy": "exclusive"},
                {"name": "VAR3", "value": "tik", "merge_policy": "append"},
            ]
        }
        p.extend(package)
        self.assertEqual(p["VAR1"], "a:gob")
        self.assertEqual(p["VAR2"], "baz")
        self.assertEqual(p["VAR3"], "tik")

    def test_cast_to_dict(self):
        d = {self.env_1a["name"]: self.env_1a["value"]}
        p = PackageEnvironment([self.env_1a])
        self.assertEqual(dict(p), d)

    def test_extend_should_fail_to_change_policy_append_to_excl(self):
        p = PackageEnvironment([self.env_1a])
        with self.assertRaises(ValueError):
            p.extend([{"name": "VAR1", "value": "baz", "merge_policy": "exclusive"}])

    def test_extend_should_fail_to_change_policy_excl_to_append(self):
        p = PackageEnvironment([self.env_3x])
        with self.assertRaises(ValueError):
            p.extend([{"name": "VAR3", "value": "baz", "merge_policy": "append"}])


class AccessTest(unittest.TestCase):
    def setUp(self):
        self.env_1a = {"name": "VAR1", "value": "a", "merge_policy": "append"}
        self.env_3x = {"name": "VAR3", "value": "c", "merge_policy": "exclusive"}

    def test_cast_to_dict(self):
        p = PackageEnvironment([self.env_1a])
        d = {self.env_1a["name"]: self.env_1a["value"]}
        self.assertEqual(dict(p), d)

    def test_empty_cast_to_empty_dict(self):
        p = PackageEnvironment()
        self.assertEqual(dict(p), {})

    def test_access_append_var(self):
        p = PackageEnvironment([self.env_1a])
        p.extend([{"name": "VAR1", "value": "b", "merge_policy": "append"}])
        self.assertEqual(p["VAR1"], "a:b")

    def test_access_exclusive_var(self):
        p = PackageEnvironment([self.env_3x])
        self.assertEqual(p["VAR3"], "c")

    def test_access_nonexistent_var_raises(self):
        p = PackageEnvironment([self.env_3x])
        with self.assertRaises(KeyError):
            p["missing"]


if __name__ == "__main__":
    unittest.main()
