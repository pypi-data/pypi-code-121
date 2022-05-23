import unittest
from test.unit.utilities.test_utils import make_test_atlas, standardise_sql_string


class TestLimit(unittest.TestCase):

    def setUp(self):
        atlas = make_test_atlas()
        test_provider = atlas.sys_connection()
        self.test_query = test_provider.select('*')

    def test_setup_view_sql(self):
        expected_sql = """@x = 
use Sys.Admin.SetupView
--provider=Test.Provider_Name
--------------

SELECT
  [Name], [Value] 
FROM
  [Sys.Connection]

enduse;

SELECT * FROM @x;"""
        setup_sql = self.test_query.setup_view("Test.Provider_Name").get_sql()
        self.assertEqual(
            standardise_sql_string(expected_sql),
            standardise_sql_string(setup_sql)
        )
