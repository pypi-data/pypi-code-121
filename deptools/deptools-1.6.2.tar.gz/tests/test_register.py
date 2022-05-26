import unittest

from deptools.register import packages_from_files, Package


class TestRegister(unittest.TestCase):
    def test_packages_from_file(self):
        packages = packages_from_files(
            ['ats-sdk-rpm_v7.5.0.zip', 'ATS-SDK-ReleaseNotes.html'])
        self.assertEqual(packages, [
            Package(os='Linux (.rpm)',
                    product_id='1018',
                    installer='ats-sdk-rpm_v7.5.0.zip',
                    readme='ATS-SDK-ReleaseNotes.html')
        ])


if __name__ == "__main__":
    unittest.main()
