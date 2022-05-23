from common.autotest.handle_allure import allure_title, allure_sub_suite, allure_severity, allure_tag, allure_suite, \
    allure_link, allure_story, allure_feature

# def story(story):
#     _StoryName, _StoryLink, jira_no = JiraPlatForm.getJiraIssueSummer(
#         story.strip())
#     if _StoryName is not None:
#         allure_story(_StoryName)
#         allure_link(_StoryLink, f'需求链接：{jira_no}')
#     def story_decorator(func):
#         @wraps(func)
#         def wrapped_function(*args, **kwargs):
#             return func(*args, **kwargs)
#         return wrapped_function
#     return story_decorator
#
# def severity(serverity):
#     allure_severity(serverity)
#     def severtity_decorator(func):
#         @wraps(func)
#         def wrapped_function(*args, **kwargs):
#             return func(*args, **kwargs)
#         return wrapped_function
#     return severtity_decorator

class AllurePlugin(object):
    @staticmethod
    def allure_title(cls,title: str) -> None:
        """allure中显示的用例标题"""
        allure_title(title)

    @staticmethod
    def allure_feature(feature: str) -> None:
        """allure中显示的用例模块"""
        allure_feature(feature)

    @staticmethod
    def allure_story(story: str) -> None:
        """allure中显示的用例模块"""
        allure_story(story)

    @staticmethod
    def allure_link(_link: str, _name=None) -> None:
        """allure中显示的用例模块"""
        allure_link(url=_link, name=_name)

    @staticmethod
    def allure_suite(_name: str) -> None:
        """allure中显示的用例模块"""
        allure_suite(_name)

    @staticmethod
    def allure_tag(_name: str) -> None:
        """allure中显示的用例模块"""
        allure_tag(_name)

    @staticmethod
    def allure_sub_suite(_name: str) -> None:
        """allure中显示的用例模块"""
        allure_sub_suite(_name)

    @staticmethod
    def allure_severity(severity_level: str) -> None:
        """allure中显示的用例等级"""
        allure_severity(severity_level)