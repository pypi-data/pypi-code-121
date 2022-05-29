import xml.dom.minidom as minidom
import xml.etree.ElementTree as ElementTree

from utils import dt, filex

FONT_FAMILY = 'sans-serif'
DEFAULT_ATTRIB_MAP = {
    'html': {
        'style': 'font-family: %s;' % FONT_FAMILY,
    },
    'svg': {
        'xmlns': 'http://www.w3.org/2000/svg',
    },
}


def render_link_styles(css_file='styles.css'):
    return _('link', None, {'rel': 'stylesheet', 'href': css_file})


def style(**kwargs):
    style_content = ''.join(list(map(
        lambda item: '%s:%s;' % (dt.to_kebab(str(item[0])), str(item[1])),
        kwargs.items(),
    )))
    return dict(style=style_content)


class _:
    def __init__(
        self,
        tag,
        child_list_or_str_or_other=None,
        attrib_custom={},
    ):
        """XML Element."""
        tag_real = tag.split('-')[0]

        attrib = DEFAULT_ATTRIB_MAP.get(tag, {})
        attrib.update(attrib_custom)
        attrib = dict(zip(
            list(map(lambda k: k.replace('_', '-'), attrib.keys())),
            list(map(str, attrib.values()))),
        )

        element = ElementTree.Element(tag_real)
        element.attrib = attrib

        if isinstance(child_list_or_str_or_other, list):
            child_list = child_list_or_str_or_other
            child_element_list = list(map(
                lambda child: child.element,
                list(filter(
                    lambda child_or_none: child_or_none is not None,
                    child_list,
                ))
            ))
            for child_element in child_element_list:
                element.append(child_element)

        elif isinstance(child_list_or_str_or_other, str):
            element.text = str(child_list_or_str_or_other)

        self.__element__ = element

    @property
    def element(self):
        return self.__element__

    def __str__(self):
        s = ElementTree.tostring(self.element, encoding='utf-8').decode()
        parsed_s = minidom.parseString(s)
        return parsed_s.toprettyxml(indent='  ')

    def __repr__(self):
        return self.__str__()

    def store(self, xml_file):
        filex.write(xml_file, str(self))
