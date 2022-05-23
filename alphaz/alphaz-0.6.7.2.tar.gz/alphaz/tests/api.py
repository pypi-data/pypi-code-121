from core import core

from alphaz.utils.api import api, Levels
from alphaz.models.tests import AlphaTest, test

from alphaz.libs import api_lib
from alphaz.utils.api import api
from alphaz.models.api import ApiMethods
from alphaz.models.main import AlphaException

log = core.get_logger("tests")

def dict_values_to_test_case(key, value_input, value_expected):
    return ({key:value_input}, {key:value_expected})
class API(AlphaTest):
    def __init__(self):
        super().__init__()

    def get_api_answer(
        self,
        route: str,
        params: dict = {},
        method: ApiMethods = ApiMethods.GET,
        data_only: bool = True,
    ):
        return api_lib.get_api_answer(
            api.get_url(local=True) + route,
            params=params,
            method=method
        )

    @test(description="Check is API is running")
    def api_up(self):
        key = "testing"
        answer = self.get_api_answer(
            route="/test/cache", params={"value": key, "reset_cache": True}
        )
        self.assert_equal(answer.error, 0)
        self.assert_is_dict_with_key_with_value(answer.data, key="value", value=key)

    @test(description="Check if the cache system is working")
    def cache(self):
        key = "testing"
        answer = self.get_api_answer(
            route="/test/cache", params={"value": key, "reset_cache": True}
        )
        self.assert_equal(answer.error, 0)
        if not "value" in answer.data:
            raise AlphaException("Empty response")

        uuid = answer.data["uuid"]
        answer = self.get_api_answer(
            route="/test/cache", params={"value": key, "reset_cache": False}
        )
        self.assert_equal(answer.error, 0)
        if not "value" in answer.data:
            raise AlphaException("Empty response")
        self.assert_equal(uuid,answer.data["uuid"])

    @test(description="Check if cache is reseted")
    def reset_cache(self):
        key = "testing"
        answer = self.get_api_answer(
            route="/test/cache", params={"value": key, "reset_cache": True}
        )
        self.assert_equal(answer.error, 0)
        if not "value" in answer.data:
            raise AlphaException("Empty response")

        uuid = answer.data["uuid"]
        answer = self.get_api_answer(
            route="/test/cache", params={"value": key, "reset_cache": True}
        )
        self.assert_equal(answer.error, 0)
        if not "value" in answer.data:
            raise AlphaException("Empty response")
        return uuid != answer.data["uuid"]

    @test(description="Test all api methods")
    def call_methods(self):
        for method in [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
        ]:
            answer = self.get_api_answer(
                route="/test/methods", method=method, params={}
            )
            #TODO: check answer
            log.info(f"Method {method} return {answer.data}")
            self.assert_equal(method, answer.data)

    @test(description="Test input parameters", level=Levels.HIGH)
    def test_parameters(self):
        default_values = {
            "list_default": [],
            "dict_default": {},
            "string_default": '',
            "integer_default": 1
        }
        tests_cases_success = [
            ({},{})
        ]
        tests_cases_success_values = [
            ("value", "value", "value"),
            ("options","Y", "Y"),
            ("list",[1,2], ['1','2']),
            ("list_str",[1,2], ['1','2']),
            ("list_int",[1,2], [1,2]),
            ("list_float",[1.1,2.2], [1.1,2.2]),
            ("list",None, None),
            ("dict",{1:"a","b":2 }, {"1":"a","b":2}),
            ("string","YYYYYY", "YYYYYY"),
            ("integer","1", 1),
            ("float",1, 1),
            ("end_like_mode","Y", "Y%"),
            ("in_like_mode","Y", "%Y%"),
            ("like_mode","*Y", "%Y"),
            ("start_like_mode","Y", "%Y"),
            ("none_mode","Y", "Y"),
        ]
        for tests_case_success_values in tests_cases_success_values:
            tests_cases_success.append(dict_values_to_test_case(*tests_case_success_values))

        tests_cases_failures = [
            ({"options":"h"}, "Wrong value <h> for parameter <options>, must be in options <['Y', 'N', 1, 2]>")
        ]

        url = api.get_url(local=True) + "/test/parameters"

        for method in ["GET", "POST"]:
            for tests_case, expected_output in tests_cases_success:
                self.assert_api_answer(url=url, method=method, expected_output=expected_output,
                    params=tests_case, default_values=default_values)

            for tests_case, expected_output in tests_cases_failures:
                self.assert_api_answer_fail(url=url, method=method, expected_output=expected_output, 
                    params=tests_case, default_values=default_values)

    @test(description="Test input parameters form url", level=Levels.HIGH)
    def test_parameters_url(self):
        default_values = {
            "list_default": [],
            "dict_default": {},
            "string_default": '',
            "integer_default": 1
        }
        
        method = "GET"
        url = api.get_url(local=True) + "/test/parameters"

        tests_cases_success_values = [
            ("value=value", {"value":"value"}),
            ("list=1,2", {"list":['1','2']}),
            ("list=1;2", {"list":['1','2']}),
            ("list_str=1,2", {"list_str":['1','2']}),
            ("list_str=1;2", {"list_str":['1','2']}),
            ("list_int=1,2", {"list_int":[1,2]}),
            ("list_int=1;2", {"list_int":[1,2]}),
            ("list_float=1.1,2.2", {"list_float":[1.1,2.2]}),
            ("list_float=1.1;2.2", {"list_float":[1.1,2.2]}),
            ('dict={"1":"a","b":2 }', {"dict":{"1":"a","b":2}}),
        ]

        for t in tests_cases_success_values:
            self.assert_api_answer(url=url + "?" + t[0], method=method, expected_output=t[1], default_values=default_values)
            
    @test(description="Test str max and min lenght parameter")
    def test_parameter_max_min_lenght(self):
        answer = self.get_api_answer(
            route="/test/parameters", method="GET", params={"string":"a"*10}
        )
        if answer.error:
            return False
        
        answer = self.get_api_answer(
            route="/test/parameters", method="GET", params={"string":"a"*120}
        )
        if not answer.error:
            return False
        answer = self.get_api_answer(
            route="/test/parameters", method="GET", params={"string":"a"}
        )
        if not answer.error:
            return False
        return True