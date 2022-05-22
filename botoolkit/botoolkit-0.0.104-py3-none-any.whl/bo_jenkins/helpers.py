from xml.dom import (
    minidom,
)
from xml.etree import (
    ElementTree,
)
from xml.etree.ElementTree import (
    Element,
)


class StandConfiguration:
    """
    Конфигурация тестового стенда
    """
    def __init__(self, url=None, branch=None, projects=None):
        self.url = url
        self.branch = branch
        self.projects = projects

    def __repr__(self):
        return (
            f'<{self.__class__.__name__} @url={self.url} @branch={self.branch} '
            f'@projects={self.projects}>'
        )

    def __str__(self):
        return self.__repr__()


def prettify_xml_element(
    element: Element,
):
    """
    Возвращает пригодную для печати XML-строку для Element
    """
    rough_string = ElementTree.tostring(
        element=element,
        encoding='utf-8',
    )

    reparsed = minidom.parseString(rough_string)

    return reparsed.toprettyxml(
        indent='  ',
    )
