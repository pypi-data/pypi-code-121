stats = [0, 0]


def pytest_assertrepr_compare(config, op, left, right):
    global stats
    stats[0] += 1


def pytest_assertion_pass(item, lineno, orig, expl):
    global stats
    stats[1] += 1


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    global stats
    terminalreporter.ensure_newline()
    terminalreporter.section("assert statistics", sep="=")
    terminalreporter.line(f"total asserts : {stats[0]}")
    if stats[0] > 0:
        terminalreporter.line(f"passed asserts: {stats[1]} ({int(100*stats[1]/stats[0])}%)")
        terminalreporter.line(f"failed asserts: {stats[0] - stats[1]} ({int(100*(stats[0] - stats[1])/stats[0])}%)")
