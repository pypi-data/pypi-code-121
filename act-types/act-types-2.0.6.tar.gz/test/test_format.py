from act.types.format import object_format


def test_tool_format():
    assert object_format("tool", "Mimikatz") == "mimikatz"
    assert object_format("tool", "Super (awesome) tool") == "super tool"


def test_threatactor_format():
    assert object_format("threatActor", "APT28") == "apt28"
    assert object_format("threatActor", "APT28 ") == "apt28"
    assert object_format("threatActor", "supER+@ta") == "super+@ta"
