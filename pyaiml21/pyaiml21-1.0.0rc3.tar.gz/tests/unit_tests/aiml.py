from pyaiml21.aiml import AIMLVersion


def test_contains():
    for version in ("1.0", "1.0.1", "2.0", "2.1"):
        assert version in AIMLVersion


def test_ordering():
    Version = AIMLVersion
    order = [Version.V1_0, Version.V1_0_1, Version.V2_0, Version.V2_1]
    assert sorted(order) == order
