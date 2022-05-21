from bs4 import BeautifulSoup
from parsers.linkedin_parser import InvalidFileName, LinkedinParser
from tests.main import BaseTest


class TestLinkedinParserPosting(BaseTest):
    def setUp(self) -> None:

        self.parser = LinkedinParser(BaseTest.load_test_config(self))

        # good_sip - defined in the test
        self.empty_sip = BeautifulSoup("", "html.parser")  # returns 'missing'
        self.bad_sip = "no soup for you"  # returns 'error'

    # jobid - export props
    def test_set_posting_jobid(self):

        good_file = "jobid_3080721373_20220516_180204.html"
        jobid = self.parser.set_posting_jobid(good_file)

        self.assertEqual(jobid, "3080721373")
        self.assertIsInstance(jobid, str)

        with self.assertRaises(TypeError):
            self.parser.set_posting_jobid()

        with self.assertRaises(InvalidFileName):
            self.parser.set_posting_jobid("")

        with self.assertRaises(InvalidFileName):
            self.parser.set_posting_jobid("nounderscores")

    # url - export prop
    def test_set_posting_url(self):

        url = self.parser.set_posting_url("3080721373")

        self.assertEqual(url, "https://www.linkedin.com/jobs/view/3080721373")
        self.assertIsInstance(url, str)

        with self.assertRaises(TypeError):
            self.parser.set_posting_url()

    # title - export prop
    def test_set_posting_title(self):

        good_sip = BeautifulSoup(
            ('<h2 class="t-24 t-bold">' "Senior DevOps Engineer" "</h2>"),
            "html.parser",
        )

        title = self.parser.set_posting_title(good_sip)
        self.assertEqual(title, "Senior DevOps Engineer")
        self.assertIsInstance(title, str)

        self.assertEqual(
            self.parser.set_posting_title(self.empty_sip), "missing"
        )

        self.assertEqual(self.parser.set_posting_title(self.bad_sip), "error")

        with self.assertRaises(TypeError):
            self.parser.set_posting_title()

    # workplace_type - export prop
    def test_set_posting_workplace_type(self):

        good_sip = BeautifulSoup(
            (
                '<span class="jobs-unified-top-card__workplace-type">'
                "Remote"
                "</span>"
            ),
            "html.parser",
        )

        workingplace_type = self.parser.set_posting_workplace_type(good_sip)
        self.assertEqual(workingplace_type, "Remote")
        self.assertIsInstance(workingplace_type, str)

        self.assertEqual(
            self.parser.set_posting_workplace_type(self.empty_sip), "missing"
        )

        self.assertEqual(
            self.parser.set_posting_workplace_type(self.bad_sip), "error"
        )

        with self.assertRaises(TypeError):
            self.parser.set_posting_workplace_type()

    # company_name - export prop
    def test_set_posting_company_name(self):

        good_sip = BeautifulSoup(
            (
                '<span class="jobs-unified-top-card__company-name">'
                '<a class="ember-view t-black t-normal"'
                'href="/company/sap/life/" id="ember146">'
                "SAP"
                "</a>"
                "</span>"
            ),
            "html.parser",
        )

        title = self.parser.set_posting_company_name(good_sip)
        self.assertEqual(title, "SAP")
        self.assertIsInstance(title, str)

        self.assertEqual(
            self.parser.set_posting_company_name(self.empty_sip), "missing"
        )

        self.assertEqual(
            self.parser.set_posting_company_name(self.bad_sip), "error"
        )

        with self.assertRaises(TypeError):
            self.parser.set_posting_company_name()

    # company_url - export prop
    def test_set_posting_company_url(self):

        good_sip = BeautifulSoup(
            (
                '<span class="jobs-unified-top-card__company-name">'
                '<a class="ember-view t-black t-normal"'
                'href="/company/sap/life/" id="ember146">'
                "SAP"
                "</a>"
                "</span>"
            ),
            "html.parser",
        )

        url = self.parser.set_posting_company_url(good_sip)
        self.assertEqual(url, "/company/sap/life/")
        self.assertIsInstance(url, str)

        with self.assertRaises(TypeError):
            self.parser.set_posting_company_url()

        self.assertEqual(
            self.parser.set_posting_company_url(self.empty_sip), "missing"
        )

        self.assertEqual(
            self.parser.set_posting_company_url(self.bad_sip), "error"
        )

    # company_details - export props
    def test_set_posting_company_details(self):

        good_sip = BeautifulSoup(
            (
                "<span>"
                '<a class="app-aware-link" href="#SALARY" target="_self">'
                "<!-- -->"
                "$80,000/yr - $125,000/yr"
                "<!-- -->"
                "</a>"
                '<span class="white-space-pre">'
                "</span>"
                " · Full-time · Mid-Senior level"
                "<!-- -->"
                "</span>"
                "<span>"
                "<!-- -->"
                "51-200 employees · Internet Publishing "
                "<!-- -->"
                "</span>"
            ),
            "html.parser",
        )

        (
            company_size,
            company_industry,
            hours,
            level,
        ) = self.parser.set_posting_company_details(good_sip)

        self.assertEqual(company_size, "51-200 employees")
        self.assertEqual(company_industry, "Internet Publishing")
        self.assertEqual(hours, "Full-time")
        self.assertEqual(level, "Mid-Senior level")

        self.assertIsInstance(company_size, str)
        self.assertIsInstance(company_industry, str)
        self.assertIsInstance(hours, str)
        self.assertIsInstance(level, str)

        with self.assertRaises(TypeError):
            self.parser.set_posting_company_details()

        self.assertEqual(
            self.parser.set_posting_company_details(self.empty_sip),
            ("missing", "missing", "missing", "missing"),
        )

        self.assertEqual(
            self.parser.set_posting_company_details(self.bad_sip),
            ("error", "error", "error", "error"),
        )

        dirty_sip = BeautifulSoup(" · one  · two  · three  · ", "html.parser")
        self.assertEqual(
            self.parser.set_posting_company_details(dirty_sip),
            ("missing", "missing", "missing", "missing"),
        )
