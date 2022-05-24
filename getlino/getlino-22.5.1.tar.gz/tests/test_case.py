import os
from atelier.test import TestCase
from subprocess import check_output, CalledProcessError

if False:
    class CaseTests(TestCase):

        def test_the_case(self):
            if 'TRAVIS' not in os.environ:
                print("Not on Travis")
                return
            if not os.environ['case']:
                print("case is not set")
                return
            getattr(self, "case" + os.environ['case'])()

        def run_shell(self, cmd, expected_exit_code=0):
            try:
                out = self.check_output(cmd.split())
            except CalledProcessError as e:
                if e.returncode == expected_exit_code:
                    return out
            else:
                if expected_exit_code == 0:
                    return out
            self.fail("{} ended with exit code {} (expected {})".format(cmd, expected_exit_code, ))

        def case1(self):
            s = self.run_shell(
            'getlino configure --batch --devtools --db-engine postgresql --usergroup travis --clone')
            self.assertEqual(s, "")

            # self.run_subprocess(['getlino', 'startsite', '--batch',
            #                      'noi', 'mysite1', '--dev-repos', 'lino noi xl'])

        def case2(self):
            self.run_shell("getlino configure --batch --db-engine postgresql --usergroup travis --clone")
            self.run_shell(['getlino', 'startsite', '--batch',
                                'noi', 'mysite1', '--dev-repos', 'lino noi xl'])

        def case3(self):
            self.run_shell(['getlino', 'configure', '--batch', '--appy', '--log-base', '--linod', '--webdav',
                                '--languages', 'en,fr,de', '--db-engine', 'mysql', '--db-port', '3306', '--usergroup', 'travis', '--clone'])
            self.run_shell(['getlino', 'startsite', '--batch',
                                'noi', 'mysite1', '--dev-repos', 'lino noi xl'])
