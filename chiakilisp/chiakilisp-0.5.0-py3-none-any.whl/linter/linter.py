# pylint: disable=line-too-long
# pylint: disable=missing-module-docstring

from chiakilisp.parser import Children

# Rules implemented right now:
#  - UnusedGlobalVariables - check the source code for unused global variables

# User could define Rules dictionary in their ~/.chiakilisp-linter-rc.cl file:
# (def Rules [... ...]) where each ... is a string representing name of a rule

# For example:
# (def Rules ["UnusedGlobalVariables"]) ;; will enable 'UnusedGlobalVariables'

_DEFAULTS = {
    'Rules': []  # no rules enabled by default, user should edit their rc file
}


class BuiltinLinter:

    """ChiakiLisp Linter"""

    _env: dict
    _wood: Children
    _config: dict
    _report: dict
    _global_variables_counts: dict

    def __init__(self, wood: Children, env: dict, config: dict = None) -> None:

        """Initializes a built-in BuiltinLinter class"""

        self._env = env
        self._wood = wood
        self._global_variables_counts = {}
        self._report = {
            'UnusedGlobalVariables': []
        }
        self._config = config or _DEFAULTS

    def report(self) -> dict:

        """Return built linter report"""

        return self._report

    def fancy_print_report(self) -> None:

        """Fancy print generated report"""

        if not self._config.get('Rules'):
            print('There are no rules to run/report')

        for rule in self._config.get('Rules'):
            print(f'>>> {rule}')
            body = self.report().get(rule)
            if not body:
                print('    ::: Nothing to report here')
            else:
                self._fancy_print_report_for_rule(rule)

    def _fancy_print_report_for_rule(self, rule) -> None:

        """Print the fancy report for the concrete rule"""

        if rule == 'UnusedGlobalVariables':
            self._fancy_print_report_for_unused_global_variables()

    def _fancy_print_report_for_unused_global_variables(self) -> None:

        for each in self._report.get('UnusedGlobalVariables'):
            print(f'    ::: Global variable \'{each}\' is not used anywhere')

    def run(self) -> None:

        """Run all implemented linter rules"""

        if 'UnusedGlobalVariables' in self._config.get('Rules'):
            self._run_check_for_unused_global_variables()

    def _run_check_for_unused_global_variables(self) -> None:

        """Rule that iterates over the wood to check for unused global variables"""

        storage = self._global_variables_counts

        for each in self._wood:
            each.lint(self._env, 'UnusedGlobalVariables', storage)

        for global_variable_name, global_variable_refer_count in storage.items():
            if not global_variable_refer_count:
                self._report['UnusedGlobalVariables'].append(global_variable_name)
