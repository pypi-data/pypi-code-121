import allure
import json

from common.plat.jira_platform import JiraPlatForm
from loguru import logger


def allure_title(title: str) -> None:
    """allure中显示的用例标题"""
    allure.dynamic.title(title)


def allure_feature(feature: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.feature(feature)

def allure_story(story: str) -> None:
    """allure中显示的用例模块,可以是Jira链接，Jira编号，Jira的名称"""
    _StoryName, _StoryLink, jira_no = JiraPlatForm.getJiraIssueSummer(
        story.strip())
    if _StoryName is None:
        _StoryName = story
    allure.dynamic.story(story)
    if _StoryLink is not None:
        allure_link(_StoryLink, f'需求链接：{jira_no}')


def allure_link(_link: str, _name=None) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.link(url=_link, name=_name)

def allure_suite(_name: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.suite(_name)

def allure_tag(_name: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.tag(_name)

def allure_sub_suite(_name: str) -> None:
    """allure中显示的用例模块"""
    allure.dynamic.sub_suite(_name)

def allure_severity(severity_level: str) -> None:
    """allure中显示的用例等级"""
    if severity_level.strip() == 'P0':
        allure_tag('冒烟测试,回归测试')
    if severity_level.strip() == 'P1':
        allure_tag('回归测试')
    if severity_level.strip() == 'P2':
        allure_tag('回归测试')
    allure.dynamic.severity(convert_severity(severity_level))


def allure_step(step: str, content: str) -> None:
    """
    :param step: 步骤及附件名称
    :param content: 附件内容
    """
    logger.info(f'{step}:{content}')
    try:
        with allure.step(step):
            allure.attach(json.dumps(content, ensure_ascii=False, indent=4), step, allure.attachment_type.TEXT)
    except Exception as e:
        logger.warning(f'{step}无用例上下文：{str}')

def convert_severity(_str):
    return _str.replace("P0", "critical").replace("P1", "normal") \
        .replace("P2", "minor").replace("P3", "trivial")







