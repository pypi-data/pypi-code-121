from typing import Any, Dict, List, Optional
from tabulate import tabulate

errors = ""
warnings = ""
table = []  # type: List[List[str]]
violations_headers = ["Test name", "Rule", "Function", "Result", "Expected"]


def addError(errors: str, testName: str, rule: str, ruleResult: str, expectedResult: str = "",
             funcName: str = "") -> str:
    errors += "Violation in " + testName + ": " + rule
    if funcName != "":
        errors += ", " + funcName
    errors += " result is " + ruleResult + "."
    if expectedResult != "":
        errors += "Should be " + expectedResult
    errors += "\n"
    return errors


def print_table(headers: List[str]) -> None:
    print(tabulate(table, headers, tablefmt="psql"))


def findExpected(funcName: str, resultsList: Dict[str, List[str]]) -> str:
    expectedResult = "\033[33mundefined\033[0m"
    for result in resultsList.keys():
        if funcName in resultsList[result]:
            expectedResult = result
            break
    return expectedResult


def appendViolation(table: List[List[str]], testName: str, actualResult: str, expectedResult: str,
                    ruleName: str = "", funcName: str = "") -> None:
    tableRow = []
    tableRow.append(testName)
    tableRow.append(ruleName)
    tableRow.append(funcName)
    tableRow.append(actualResult)
    tableRow.append(expectedResult)

    table.append(tableRow)


# compare jar results with expected
# @param rulesResults is a dictionary that includes all the rule names and their results from the jar output
# @param expectedRulesResults is a dictionary that includes all the rule names and their results from tester file
# @param assertMessages is a dictionary that includes all the rule names and their assertion messages
#        from the jar output
# @param expectedAssertionMessages is a dictionary that includes all the rule names and their assertion messages
#        from tester file
# @param test is a boolean indicator of current test (test==false <=> at least one error occured)
def compareResultsWithExpected(
        testName: str,
        rulesResults: Dict[str, Any],
        expectedRulesResults: Dict[str, Any],
        assertMessages: Dict[str, Any],
        expectedAssertionMessages: Optional[Dict[str, Any]],
        test: bool = True
) -> bool:
    global errors
    global warnings

    if rulesResults != expectedRulesResults:
        for rule in rulesResults.keys():
            ruleResult = rulesResults[rule]
            if rule in expectedRulesResults.keys():
                if isinstance(ruleResult, str):  # flat rule ( ruleName: result )
                    if ruleResult != expectedRulesResults[rule]:
                        test = False
                        # errors = addError(errors, testName, rule, ruleResult, expectedRulesResults[rule])
                        appendViolation(table, testName, rulesResults[rule], expectedRulesResults[rule], rule, "")

                else:  # nested rule ( ruleName: {result1: [funcionts list], result2: [funcionts list] ... } )
                    for result, funcList in ruleResult.items():
                        funcList.sort()
                        expectedRulesResults[rule][result].sort()

                        # compare functions sets (current results with expected)
                        if funcList != expectedRulesResults[rule][result]:
                            for funcName in funcList:
                                # if funcion appears in current results but does not appear in the expected ones
                                if funcName not in expectedRulesResults[rule][result]:
                                    test = False
                                    # errors = addError(errors, testName, rule, result, "", funcName)
                                    expectedResult = findExpected(funcName, expectedRulesResults[rule])
                                    appendViolation(table, testName, result, expectedResult, rule, funcName)
            else:
                test = False
                result = (rulesResults[rule]
                          if isinstance(ruleResult, str)
                          else "Object{" + ", ".join(rulesResults[rule].keys()) + "}")
                appendViolation(table, testName, result, "\033[33mundefined\033[0m", rule, "")
                # errors += testName + ", " + rule + " is not listed in 'rules'. Expected rules: " + \
                # ','.join(expectedRulesResults.keys()) + "\n"

    # if assertMessages field is defined (in tester)
    if expectedAssertionMessages:
        for rule in expectedAssertionMessages.keys():
            if rule not in assertMessages:  # current rule is missing from 'assertMessages' section in current results
                test = False
                errors += testName + ", rule \"" + rule + \
                    "\" does not appear in the output. Please, remove unnecessary rules.\n"
            elif expectedAssertionMessages[rule] != assertMessages[rule]:
                # assertion messages are different from each other
                test = False
                errors += testName + ", rule \"" + rule + "\": wrong assertion message. Got: \"" + \
                    assertMessages[rule] + "\". Expected: \"" + expectedAssertionMessages[rule] + "\".\n"
    return test


def get_errors() -> str:
    return errors


def has_violations() -> bool:
    if table:
        return True
    else:
        return False


def get_violations() -> None:
    if table:
        print("Found violations:")
        print_table(violations_headers)
