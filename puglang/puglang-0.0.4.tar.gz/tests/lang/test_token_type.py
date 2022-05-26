from puglang.lang.token_type import TokenType


def test_each_token_type_value():
    assert TokenType.IDENTIFIER.value == 0
