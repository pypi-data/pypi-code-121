"""
Expectations
^^^^^^^^^^^^

Base classes for expectation and manager, and
builtin expectations.

"""

from .exceptions import *

################################
# Helper
################################
def all_subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c)]
    )


################################
# Main Classes
################################
class ExpectationResultBase(object):
    """
    Class to return one or more results from an
    expectation validation step.
    """

    def __init__(self, *args, **kwargs):
        self.results = []

    def add_result(self, expectation, description, passed, extra={}):
        """
        Add an entry to the validation result object

        Args:
           expectation: Name of the expectation
           description: One line summary of the check
           passed: True if the check has passed
           extra: Dictionary with extra context including reason

        """
        if not isinstance(passed, bool):
            raise IncorrectImplementationExpectation(
                "Expectation requires 'passed' to be boolean"
            )

        if not isinstance(expectation, str):
            raise IncorrectImplementationExpectation(
                "Expectation require name to be string"
            )

        if not isinstance(description, str):
            raise IncorrectImplementationExpectation(
                "Expectation require description to be string"
            )

        if not isinstance(extra, dict):
            raise IncorrectImplementationExpectation(
                "Expectation require 'extra' to be dict"
            )

        entry = {
            "expectation": expectation,
            "description": description,
            "passed": passed,
            "extra": extra,
        }

        self.results.append(entry)

    def get_results(self):
        for r in self.results:
            yield r


class ExpectationBase(object):
    """
    Base class for expectations
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the base class for expectations
        """
        self.name = "unknown_table_check"
        self.description = "Unknown description"

    def match(self, config):
        """
        Check if the expectations matches

        Args:
           config: Expectation specification

        Returns:
           True if this class can handle expectation

        """
        if not isinstance(config, dict):
            return False

        return config.get("expectation", None) == self.name

    def args_validator_attrs_list(self, config, attrs):
        params = config.get("params", {})
        for attr in attrs:
            if attr not in params:
                raise InvalidExpectation("Missing parameter: {}".format(attr))

    def validate_args(self, config):
        """
        Validate arguments passed to this expectation

        Check if the expectation is correctly specified beyond the
        name

        Args:
           config: Expectation specification

        Returns:
           True if this class can handle this specification

        """
        pass

    def generate(self, df):
        return []

    def validate(self, df, config):

        result = ExpectationResultBase()
        result.add_result(
            expectation=self.name, description=self.description, passed=True
        )
        return result


# Output of GreatExpectations
# {
#    "expectation_type": "expect_table_row_count_to_be_between",
#    "kwargs": {
#        "min_value": 0,
#        "max_value": None
#    },
#    "meta": {
#        "BasicDatasetProfiler": {
#            "confidence": "very low"
#        }
#    }
# }


class ExpectationManagerBase(object):
    def __init__(self):
        self.subclasses = None

    def initialize(self):
        subclasses = all_subclasses(ExpectationBase)
        self.subclasses = [cls() for cls in subclasses]

    def validate(self, df, expectations):

        if self.subclasses is None:
            raise NotInitialized("Manager not initialized")

        if (not isinstance(expectations, list)) and (
            not isinstance(expectations, dict)
        ):
            raise InvalidExpectation("Expectations should be a list or dict")

        if isinstance(expectations, dict):
            expectations = [expectations]

        if len(expectations) == 0:
            raise NoExpectations("Empty list")

        for e in expectations:
            if (not isinstance(e, dict)) or ("expectation" not in e):
                raise InvalidExpectation("Invalid expectation format")

        result = []
        for e in expectations:
            nomatches = True
            name = e["expectation"]
            for cls in self.subclasses:
                if cls.match(e):
                    cls.validate_args(e)

                    nomatches = False

                    # Now run the validation
                    expectationresult = cls.validate(df, e)

                    if (expectationresult is None) or (
                        not isinstance(expectationresult, ExpectationResultBase)
                    ):
                        raise IncorrectImplementationExpectation(
                            "Expectation returned None or unexpected object"
                        )

                    # Now all the validation results should be added to the common list.
                    result.extend(list(expectationresult.get_results()))

            if nomatches:
                raise UnsupportedExpectation("No handler for {}".format(name))

        return result
