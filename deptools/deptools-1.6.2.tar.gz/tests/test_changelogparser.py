import datetime
import unittest

from deptools import changelogparser as clp

CHANGELOGTEXT = r"""# AlazarTech Deployment Tools Change Log

This file contains all important changes to the AlazarTech deployment tools

## [Unreleased]

## [0.0.2] - 2019-01-25
### Fixed
- [Internal] Make directory copy work even if destination already exists

## [0.0.1] - 2019-01-23
### Added
- Initial version: deploy.py [#3]
- Look at this other problem [libats#123]
- This solves many things. Line
  break. [libats#123, #34]

"""

CHANGELOG = clp.ChangeLog(
    "AlazarTech Deployment Tools Change Log",
    "This file contains all important changes to the AlazarTech deployment tools",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(True, 0, 0, 0, "", ""),
                            datetime.date.today(), False), []),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 2, "", ""),
                            datetime.date(2019, 1, 25), False),
            [
                clp.CategoryLog(clp.EntryType.Fixed, [
                    clp.EntryLog(
                        True,
                        "Make directory copy work even if destination already exists",
                        [],
                    ),
                ])
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(
                False, 0, 0, 1, "", ""), datetime.date(2019, 1, 23), False), [
                    clp.CategoryLog(clp.EntryType.Added, [
                        clp.EntryLog(False, "Initial version: deploy.py",
                                     [clp.TicketRef(3, None)]),
                        clp.EntryLog(False, "Look at this other problem",
                                     [clp.TicketRef(123, "libats")]),
                        clp.EntryLog(False,
                                     "This solves many things. Line break.", [
                                         clp.TicketRef(123, "libats"),
                                         clp.TicketRef(34, None)
                                     ])
                    ]),
                ]),
    ],
)

CHANGELOGTEXT2 = r"""# Net List Extractor Change Log

## [1.3.0] - 2019-03-19
### Added
- Support for forward slashes "/" in net name

## [1.2.0] - 2019-03-19 [YANKED]
### Changed
- Use net name in exported file

## [1.1.0] - 2019-03-19
### Added
- Error message window on failed parse

## [1.0.0] - 2019-03-18
### Added
- Initial version
"""

CHANGELOG2 = clp.ChangeLog(
    "Net List Extractor Change Log",
    "",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 1, 3, 0, "", ""),
                            datetime.date(2019, 3, 19), False),
            [
                clp.CategoryLog(clp.EntryType.Added, [
                    clp.EntryLog(
                        False, "Support for forward slashes \"/\" in net name",
                        []),
                ]),
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 1, 2, 0, "", ""),
                            datetime.date(2019, 3, 19), True),
            [
                clp.CategoryLog(clp.EntryType.Changed, [
                    clp.EntryLog(False, "Use net name in exported file", []),
                ]),
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(
                False, 1, 1, 0, "", ""), datetime.date(2019, 3, 19), False), [
                    clp.CategoryLog(clp.EntryType.Added, [
                        clp.EntryLog(
                            False, "Error message window on failed parse", []),
                    ]),
                ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 1, 0, 0, "", ""),
                            datetime.date(2019, 3, 18), False), [
                                clp.CategoryLog(clp.EntryType.Added, [
                                    clp.EntryLog(False, "Initial version", []),
                                ]),
                            ]),
    ],
)

CHANGELOGTEXT3 = r"""# Net List Extractor Change Log

## [1.2.0-rc2+12] - 2019-03-19
### Added
- Support for forward slashes "/" in net name

## [1.2.0+12] - 2019-03-19
### Changed
- Use net name in exported file

## [1.2.0-1] - 2019-03-19
### Added
- Error message window on failed parse
"""

CHANGELOG3 = clp.ChangeLog(
    "Net List Extractor Change Log",
    "",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 1, 2, 0, "rc2", "12"),
                            datetime.date(2019, 3, 19), False),
            [
                clp.CategoryLog(clp.EntryType.Added, [
                    clp.EntryLog(
                        False, "Support for forward slashes \"/\" in net name",
                        []),
                ]),
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 1, 2, 0, "", "12"),
                            datetime.date(2019, 3, 19), False),
            [
                clp.CategoryLog(clp.EntryType.Changed, [
                    clp.EntryLog(False, "Use net name in exported file", []),
                ]),
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(
                False, 1, 2, 0, "1", ""), datetime.date(2019, 3, 19), False), [
                    clp.CategoryLog(clp.EntryType.Added, [
                        clp.EntryLog(
                            False, "Error message window on failed parse", []),
                    ]),
                ]),
    ],
)

CHANGELOGA = clp.ChangeLog(
    "AlazarTech Deployment Tools Change Log",
    "This file contains all important changes to the AlazarTech deployment tools",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(True, 0, 0, 0, "", ""),
                            datetime.date.today(), False), []),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 2, "", ""),
                            datetime.date(2019, 1, 25), False),
            [
                clp.CategoryLog(clp.EntryType.Fixed, [
                    clp.EntryLog(
                        True,
                        "Make directory copy work even if destination already exists",
                        []),
                ])
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(
                False, 0, 0, 1, "", ""), datetime.date(2019, 1, 23), False), [
                    clp.CategoryLog(clp.EntryType.Added, [
                        clp.EntryLog(False, "Initial version: deploy.py", []),
                    ])
                ]),
    ],
)

CHANGELOGB = clp.ChangeLog(
    "random test",
    "This text should get dropped while merging",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(True, 0, 0, 0, "", ""),
                            datetime.date.today(), False), [
                                clp.CategoryLog(clp.EntryType.Fixed, [
                                    clp.EntryLog(True, "An entry here", []),
                                ])
                            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 3, "", ""),
                            datetime.date(2019, 1, 26), False), [
                                clp.CategoryLog(clp.EntryType.Fixed, [
                                    clp.EntryLog(False, "Another here", []),
                                ])
                            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 1, "", ""),
                            datetime.date(2019, 1, 22), False), [
                                clp.CategoryLog(clp.EntryType.Added, [
                                    clp.EntryLog(False, "Third entry", []),
                                ])
                            ]),
    ],
)

CHANGELOGMERGED = clp.ChangeLog(
    "AlazarTech Deployment Tools Change Log",
    "This file contains all important changes to the AlazarTech deployment tools",
    [
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(True, 0, 0, 0, "", ""),
                            datetime.date.today(), False), [
                                clp.CategoryLog(clp.EntryType.Fixed, [
                                    clp.EntryLog(True, "An entry here", []),
                                ])
                            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 3, "", ""),
                            datetime.date(2019, 1, 26), False), [
                                clp.CategoryLog(clp.EntryType.Fixed, [
                                    clp.EntryLog(False, "Another here", []),
                                ])
                            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(False, 0, 0, 2, "", ""),
                            datetime.date(2019, 1, 25), False),
            [
                clp.CategoryLog(clp.EntryType.Fixed, [
                    clp.EntryLog(
                        True,
                        "Make directory copy work even if destination already exists",
                        []),
                ])
            ]),
        clp.VersionLog(
            clp.VersionInfo(clp.VersionNumber(
                False, 0, 0, 1, "", ""), datetime.date(2019, 1, 23), False), [
                    clp.CategoryLog(clp.EntryType.Added, [
                        clp.EntryLog(False, "Initial version: deploy.py", []),
                        clp.EntryLog(False, "Third entry", []),
                    ]),
                ]),
    ],
)


class TestChangeLog(unittest.TestCase):

    def test_parse(self):
        self.assertEqual(clp.ChangeLogRuleVisitor().parse(CHANGELOGTEXT),
                         CHANGELOG)
        self.assertEqual(clp.ChangeLogRuleVisitor().parse(CHANGELOGTEXT2),
                         CHANGELOG2)
        self.assertEqual(clp.ChangeLogRuleVisitor().parse(CHANGELOGTEXT3),
                         CHANGELOG3)

    def test_merge(self):
        self.assertEqual(clp.changelogs_merge([CHANGELOGA]), CHANGELOGA)
        self.assertEqual(clp.changelogs_merge([CHANGELOGA, CHANGELOGB]),
                         CHANGELOGMERGED)

    def test_version(self):
        self.assertEqual(clp.changelog_version(CHANGELOG),
                         clp.VersionNumber(True, 0, 0, 0, "", ""))

    def test_html(self):
        self.assertEqual(
            clp.changelog_to_html(CHANGELOG),
            """<h1>AlazarTech Deployment Tools Change Log</h1>
<p>This file contains all important changes to the AlazarTech deployment tools</p>
<h2>[Unreleased]</h2>
<ul><li>No user-visible change</li></ul>
<h2>[0.0.2] - 2019-1-25</h2>
<ul><li>No user-visible change</li></ul>
<h2>[0.0.1] - 2019-1-23</h2>
<h3>Added</h3>
<ul>
    <li>Initial version: deploy.py</li>
    <li>Look at this other problem</li>
    <li>This solves many things. Line break.</li>
</ul>
""")

    def test_md(self):
        self.assertEqual(
            clp.changelog_to_md(CHANGELOG, True),
            """# AlazarTech Deployment Tools Change Log

This file contains all important changes to the AlazarTech deployment tools

## [Unreleased]
- No user-visible change

## [0.0.2] - 2019-01-25
### Fixed
- [Internal] Make directory copy work even if destination already exists

## [0.0.1] - 2019-01-23
### Added
- Initial version: deploy.py [#3]
- Look at this other problem [libats#123]
- This solves many things. Line break. [libats#123, #34]
""")

    def test_deb(self):
        self.assertEqual(
            clp.changelog_to_deb(CHANGELOG, "deptools"),
            """deptools (0.0.0) UNRELEASED; urgency=medium

  * No user-visible change

 -- AlazarTech <support@alazartech.com>  {} 12:12:00 -0400

deptools (0.0.2) UNRELEASED; urgency=medium

  * No user-visible change

 -- AlazarTech <support@alazartech.com>  Fri, 25 Jan 2019 12:12:00 -0400

deptools (0.0.1) UNRELEASED; urgency=medium

  * Added: Initial version: deploy.py
  * Added: Look at this other problem
  * Added: This solves many things. Line break.

 -- AlazarTech <support@alazartech.com>  Wed, 23 Jan 2019 12:12:00 -0400

""".format(datetime.date.today().strftime('%a, %d %b %Y')))

    def test_spec(self):
        self.assertEqual(
            clp.expand_spec(CHANGELOG, "@VERSION@ test\n", True),
            """Unreleased test
* {} AlazarTech <support@alazartech.com>
- Version Unreleased
- No user-visible change
* Fri Jan 25 2019 AlazarTech <support@alazartech.com>
- Version 0.0.2
- Fixed: Make directory copy work even if destination already exists
* Wed Jan 23 2019 AlazarTech <support@alazartech.com>
- Version 0.0.1
- Added: Initial version: deploy.py [#3]
- Added: Look at this other problem [libats#123]
- Added: This solves many things. Line break. [libats#123, #34]
""".format(datetime.date.today().strftime('%a %b %d %Y')))

    def test_unordered(self):
        BadVersionLog = clp.ChangeLog("", "", [
            clp.VersionLog(
                clp.VersionInfo(clp.VersionNumber(False, 0, 0, 1, "", ""),
                                datetime.date.today(), False), []),
            clp.VersionLog(
                clp.VersionInfo(clp.VersionNumber(False, 0, 0, 2, "", ""),
                                datetime.date(2019, 1, 25), False), [])
        ])
        self.assertRaises(ValueError,
                          lambda: clp.check_date_and_version_ordering(BadVersionLog))
        BadDateLog = clp.ChangeLog("", "", [
            clp.VersionLog(
                clp.VersionInfo(clp.VersionNumber(False, 0, 0, 2, "", ""),
                                datetime.date(2022, 4, 3), False), []),
            clp.VersionLog(
                clp.VersionInfo(clp.VersionNumber(False, 0, 0, 1, "", ""),
                                datetime.date(2022, 4, 4), False), [])
        ])
        self.assertRaises(ValueError,
                          lambda: clp.check_date_and_version_ordering(BadDateLog))


if __name__ == "__main__":
    unittest.main()
