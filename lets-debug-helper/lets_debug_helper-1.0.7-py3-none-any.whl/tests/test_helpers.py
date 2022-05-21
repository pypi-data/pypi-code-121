#!/usr/bin/env python3
import argparse
import unittest

from parameterized import parameterized

from letsdebughelper.helpers import ValidateArgRegex, Ctext


class TestHelpers(unittest.TestCase):

    @parameterized.expand([
        ('testdomain.com', 'testdomain.com'),
        ('.testdomain.com', '.testdomain.com'),
        ('*.testdomain.com', '*.testdomain.com'),
        ('sub-site.testdomain.com', 'sub-site.testdomain.com'),
        ('sub.sub.testdomain.com', 'sub.sub.testdomain.com'),
    ])
    def test_correct_validate_domain_arg_regex(self, domain, expected):
        """Helpers: Test correct domain regex"""
        actual = ValidateArgRegex('domain')(domain)
        self.assertEqual(actual, expected)

    def test_bad_validate_domain_arg_regex(self):
        """Helpers: Test bad domain regex"""
        domain = 'testdomainthatiswrong'
        with self.assertRaises(argparse.ArgumentTypeError):
            ValidateArgRegex('domain')(domain)

    def test_wrong_arg(self):
        """Helpers: Test bad domain regex"""
        domain = 'testdomainthatiswrong'
        with self.assertRaises(KeyError):
            ValidateArgRegex('wrong')(domain)

    def test_get_color_invalid(self):
        """An invalid color choice will raise an exception"""
        with self.assertRaises(AttributeError) as context:
            Ctext.FAKECOLOR('text')

        self.assertIn('"FAKECOLOR" is not available', str(context.exception), 'Failed to catch the intended exception')

    def test_set_custom_color(self):
        """Ensure that a new custom color can be set"""
        Ctext.custom = 'fake-color'
        self.assertEqual(Ctext.colors['custom'], 'fake-color')

    def test_color_returned(self):
        """Ensure that the color + string + default are returned"""
        expected = Ctext.colors['red'] + 'fake-string' + Ctext.colors['default']
        self.assertEqual(expected, Ctext.red('fake-string'))

    def test_custom_color_returned(self):
        """Ensure that the new color is returned properly after being set"""
        Ctext.colors['new-color'] = 'fake-color'
        expected = Ctext.colors['new-color'] + 'fake-string' + Ctext.colors['default']
        self.assertEqual(expected, Ctext['new-color']('fake-string'))
