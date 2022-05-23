from common.autotest.handle_assert import assert_result, assert_equals, assert_contains, assert_Nobank, \
    assert_not_contains, assert_scene_result, assert_excel_contain, assert_equal, assert_response, \
    assert_contain_response


class AssertPlugin(object):
    @classmethod
    def assert_result(self, res: dict, expect_str: str='断言检查'):
        """ 预期结果实际结果断言方法
           :param res: 实际响应结果
           :param expect_str: 预期响应内容，从excel中读取
           return None
           """
        assert_result(res, expect_str)

    @classmethod
    def assert_response(self,res,expect_str: str='断言检查'):
        assert_response(res, expect_str)

    @classmethod
    def assert_equal(self, res, expect_str,desc:str='断言检查'):
        assert_equal(res, expect_str, desc)

    @classmethod
    def assert_excel_contain(self, res: dict, expect_str: str='断言检查'):
        assert_excel_contain(res, expect_str)

    @classmethod
    def assert_contain_response(self, res, expect_str: str='断言检查'):
        assert_contain_response(res, expect_str)

    @classmethod
    def assert_equals(self, res, expect_str,desc:str='断言检查'):
        assert_equals(res, expect_str, desc)

    @classmethod
    def assert_contains(self, res, expect_str, desc:str='断言检查'):
        assert_contains(res, expect_str, desc)

    @classmethod
    def assert_Nobank(self, res, desc:str='断言检查'):
        assert_Nobank(res, desc)

    @classmethod
    def assert_not_contains(self, res, expect_str,desc:str='断言检查'):
        assert_not_contains(res, expect_str, desc)

    @classmethod
    def assert_scene_result(self, res, expect_dict):
        assert_scene_result(res,expect_dict)



