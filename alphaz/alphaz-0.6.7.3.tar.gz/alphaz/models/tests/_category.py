from typing import Dict

from ...libs import dict_lib

from ._group import TestGroup


class TestCategory:
    def __init__(self, category):
        self.category = category

        self.groups: Dict[str, TestGroup] = {}

    def add_test_group(self, testGroup: TestGroup):
        self.groups[testGroup.name] = testGroup

    def test_all(self):
        for group_name, test_group in self.groups.items():
            test_group.test_all()

    def save_all(self):
        for group_name, test_group in self.groups.items():
            test_group.save_all()

    def print(self, output=True):
        txt = ""
        for group_name, test_group in self.groups.items():
            txt += "\n__________ %s __________\n\n" % group_name
            txt += test_group.print(output=False)
        if output:
            print(txt)
        return txt

    def get_tests_groups_names(self):
        return list(self.groups.keys())

    def get_test_group(self, name):
        return self.groups[name]

    def to_json(self):
        return self.groups


class TestCategories:
    def __init__(self):
        self.categories: Dict[str, TestCategory] = {}

    def add_test_group(self, test_group: TestGroup):
        if not test_group.category in self.categories:
            self.categories[test_group.category] = TestCategory(test_group.category)

        self.categories[test_group.category].add_test_group(test_group)

        self.categories = dict_lib.sort_dict(self.categories)

    def resume(self):
        contents = []
        space = "   "
        c_space = "      "
        g_space = "         "

        failed, success, times = [], [], 0
        l_content = []

        for category_name, category in self.categories.items():
            c_failed, c_success, c_times = [], [], 0
            c_content = []

            for group_name, group in category.groups.items():
                g_failed, g_success, g_times = [], [], 0
                g_content = []

                for test_name, test in group.tests.items():
                    if test.disable:
                        continue
                    stdout = test.last_run_elapsed
                    stderr = str(test.ex) if test.ex is not None else None

                    g_times += test.elapsed
                    c_times += test.elapsed
                    times += test.elapsed
                    if not test.status:
                        g_failed.append((category_name, group_name, test_name))
                        c_failed.append((category_name, group_name, test_name))
                        failed.append((category_name, group_name, test_name))
                    else:
                        g_success.append((category_name, group_name, test_name))
                        c_success.append((category_name, group_name, test_name))
                        success.append((category_name, group_name, test_name))

                for fail in g_failed:
                    g_content.append(f"{g_space} - {fail[2]}")
                if len(g_failed) != 0:
                    g_content.append(f"{g_space}Failed:")
                g_content.append(
                    f"{c_space}- {group_name}: {len(g_success)} success, {len(g_failed)} failed, in {g_times}"
                )

                contents.extend(g_content[::-1])

            for fail in c_failed:
                c_content.append(f"{c_space} - {fail[1]}/{fail[2]}")
            if len(c_failed) != 0:
                c_content.append(f"{c_space}Failed:")

            c_content.append(
                f"{space}- {category_name}: {len(c_success)} success, {len(c_failed)} failed, in {c_times}"
            )

            contents.extend(c_content[::-1])

        for fail in failed:
            l_content.append(f"{space} - {fail[0]}/{fail[1]}/{fail[2]}")
        if len(failed) != 0:
            l_content.append(f"{space}Failed:")
        l_content.append(
            f"- Total: {len(success)} success, {len(failed)} failed, in {times}"
        )
        contents.extend(l_content[::-1])
        print("\n".join(contents))

    def to_json(self):
        return self.categories

    def to_junit(self, file_path):
        if not "." in file_path:
            file_path += ".xml"
        from junit_xml import TestSuite, TestCase

        suites = []
        for category_name, category in self.categories.items():
            test_cases = []
            for group_name, group in category.groups.items():
                for test_name, test in group.tests.items():
                    stdout = test.last_run_elapsed
                    stderr = str(test.ex) if test.ex is not None else None
                    test_case = TestCase(
                        test_name,
                        group_name,
                        test.elapsed,
                        stdout,
                        stderr,
                        timestamp=test.end_time,
                        status=test.status,
                    )
                    if test.disable:
                        continue
                    if not test.ex:
                        test_case.add_error_info(
                            message=test.ex, error_type=type(test.ex)
                        )
                    if not test.status:
                        test_case.add_failure_info(message="failed")
                    test_cases.append(test_case)
            suites.append(TestSuite(category_name, test_cases))

        with open(file_path, "w") as f:
            f.write(TestSuite.to_xml_string(suites))
