import abc
import copy
import os
import pathlib

SPACER = '  '


class HtmlItem(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_style(self, depth):
        pass

    @abc.abstractmethod
    def get_body(self, depth):
        pass


class Html:
    def __init__(self):
        self.__html_items = []

    def to_string(self):
        rtn = '<html>\n'
        rtn += '{}<style>\n'.format(SPACER)
        for html_item in self.__html_items:
            style = html_item.get_style(depth=2)
            if style.strip() != '':
                rtn += html_item.get_style(depth=2) + '\n'
        rtn += '{}</style>\n'.format(SPACER)
        for html_item in self.__html_items:
            rtn += html_item.get_body(depth=1) + '\n'
        rtn += '</html>\n'
        return rtn

    def append(self, html_item):
        if issubclass(html_item.__class__, HtmlItem):
            self.__html_items.append(html_item)
        else:
            raise Exception('object is not a HtmlItem')


class HtmlFooter(HtmlItem):
    def __init__(self, html_items):
        for html_item in html_items:
            if not issubclass(html_item.__class__, HtmlItem):
                raise Exception('object is not a HtmlItem')
        self.html_items = html_items

    def get_style(self, depth):
        rtn = ''
        for html_item in self.html_items:
            rtn += html_item.get_body() + '\n'
        return rtn

    def get_body(self, depth):
        rtn = '<footer>\n'
        for html_item in self.html_items:
            rtn += html_item.get_body() + '\n'
        rtn += '</footer>\n'
        return rtn


class HtmlList(HtmlItem):
    def __init__(self, html_items, ordered=True):
        for html_item in html_items:
            if not issubclass(html_item.__class__, HtmlItem):
                raise Exception('object is not a HtmlItem')
        self.html_items = html_items
        self.ordered = ordered

    def get_style(self, depth):
        rtn = ''
        for item in self.html_items:
            rtn += item.get_style(depth)
        return rtn

    def get_body(self, depth):
        rtn = ''
        for item in self.html_items:
            rtn += '{}<li>{}</li>\n'.format(SPACER * (depth + 1), item.get_body(0))
        if self.ordered:
            rtn = '{}<ol>\n{}{}</ol>'.format(SPACER * depth, rtn, SPACER * depth)
        else:
            rtn = '{}<ul>\n{}{}</ul>'.format(SPACER * depth, rtn, SPACER * depth)
        return rtn


class HtmlCode(HtmlItem):
    def __init__(self, text):
        self.text = text

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        text = self.text.replace('\n', '<br>\n' + SPACER * (depth+1))
        return '{}<code>\n{}{}\n{}</code>'.format(SPACER * depth, SPACER * (depth + 1), text, SPACER * depth)


class HtmlText(HtmlItem):
    def __init__(self, text, bold=False, italicized=False, centered=False, heading_level=None,
                 paragraph=None, font=None):
        self.text = text
        self.bold = bold
        self.italicized = italicized
        self.centered = centered
        self.heading_level = heading_level
        self.paragraph = paragraph
        self.font = font

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        text = self.text.replace('\n', '<br>\n' + SPACER * (depth+1))
        if self.font is None:
            rtn = text
        else:
            rtn = self.font.to_string(text)
        if self.bold:
            rtn = '<b>{}</b>'.format(rtn)
        if self.italicized:
            rtn = '<i>{}</i>'.format(rtn)
        if self.centered:
            rtn = '<c>{}</c>'.format(rtn)
        if self.heading_level:
            rtn = '<h{}>{}</h{}>'.format(self.heading_level, rtn, self.heading_level)
        if self.paragraph:
            rtn = '<p>{}</p>'.format(rtn)
        return SPACER * (depth + 1) + rtn


class HtmlTable(HtmlItem):
    def __init__(self, data, column_headings=None, border=None, border_collapse=None,
                 font_family=None, width=None, text_align=None, padding=None,
                 even_background_color=None,
                 odd_background_color=None):
        self.data = data
        self.column_headings = column_headings
        self.border_collapse = border_collapse
        self.border = border
        self.font_family = font_family
        self.width = width
        self.text_align = text_align
        self.padding = padding
        self.even_background_color = even_background_color
        self.odd_background_color = odd_background_color

    def add_row(self, row):
        self.data.append(row)

    def get_style(self, depth):
        rtn = ''
        rtn += '{}table {{\n'.format(SPACER * depth)
        if self.font_family is not None:
            rtn += '{}font-family: {};\n'.format(SPACER * (depth + 1), self.font_family)
        if self.border_collapse is not None:
            rtn += '{}border-collapse: {};\n'.format(SPACER * (depth + 1), self.border_collapse)
        if self.width is not None:
            rtn += '{}width: {};\n'.format(SPACER * (depth + 1), self.width)
        rtn += '{}}}\n'.format(SPACER * depth)
        rtn += '{}td, th {{\n'.format(SPACER * depth)
        if self.border is not None:
            rtn += '{}border: {};\n'.format(SPACER * (depth + 1), self.border)
        if self.text_align is not None:
            rtn += '{}text-align: {};\n'.format(SPACER * (depth + 1), self.text_align)
        if self.padding is not None:
            rtn += '{}padding: {}\n'.format(SPACER * (depth + 1), self.padding)
        rtn += '{}}}'.format(SPACER * depth)
        return rtn

    def get_body(self, depth):
        rtn = ''
        rtn += '{}<table>\n'.format(SPACER * depth)
        if self.column_headings is not None:
            rtn += '{}<tr>\n'.format(SPACER * (depth + 1))
            for heading in self.column_headings:
                rtn += '{}<th>{}</th>\n'.format(SPACER * (depth + 2), heading)
            rtn += '{}</tr>\n'.format(SPACER * (depth + 1))
        line_number = 0
        for row in self.data:
            rtn += '{}<tr>\n'.format(SPACER * (depth + 1))
            for cell in row:
                bg_color = ''
                if line_number % 2:
                    if self.even_background_color:
                        bg_color = ' bgcolor={}'.format(self.even_background_color)
                else:
                    if self.odd_background_color:
                        bg_color = ' bgcolor={}'.format(self.odd_background_color)
                rtn += '{}<td{}>{}</td>\n'.format(SPACER * (depth + 2), bg_color, cell)
            rtn += '{}</tr>\n'.format(SPACER * (depth + 1))
            line_number += 1
        rtn += '{}</table>'.format(SPACER * depth)
        return rtn


class HtmlBreak(HtmlItem):
    def __init__(self):
        pass

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        return '{}<br>'.format(SPACER * depth)


class HtmlLine(HtmlItem):
    def __init__(self):
        pass

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        return '<hr>'


class HtmlImage(HtmlItem):
    def __init__(self, image, alt_text=None, height=None, width=None):
        self.image = image
        self.alt_text = alt_text
        self.height = height
        self.width = width

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        if self.alt_text:
            alt_text = ' alt="{}"'.format(self.alt_text)
        else:
            alt_text = ''
        if self.height:
            height = ' height="{}"'.format(self.height)
        else:
            height = ''
        if self.width:
            width = ' width="{}"'.format(self.width)
        else:
            width = ''
        return '<img src="{}"{}{}{}>'.format(self.image, alt_text, height, width)


class HtmlLink(HtmlItem):
    def __init__(self, link, text):
        self.link = link
        self.text = text

    def get_style(self, depth):
        return ''

    def get_body(self, depth):
        return '{}<a href="{}">{}</a>'.format(SPACER * depth, self.link, self.text)


class HtmlMailTo(HtmlLink):
    def __init__(self, email, user_name):
        super(HtmlLink, self).__init__()
        self.link = 'mailto:{}'.format(email)
        self.text = user_name


class Font:
    def __init__(self, color=None, size=None, face=None):
        self.color = color
        self.size = size
        self.face = face

    def to_string(self, text):
        rtn = '<font'
        if self.size is not None:
            rtn += ' size="{}"'.format(self.size)
        if self.color is not None:
            rtn += ' color="{}"'.format(self.color)
        if self.face is not None:
            rtn += ' face="{}"'.format(self.face)
        rtn += '>{}</font>'.format(text)
        return rtn


def main():
    file_name = 'test.html'
    with open(file_name, 'w') as the_file:
        html = Html()
        values = [HtmlText('first', bold=True), HtmlText('second'), HtmlText('third')]
        ol = HtmlList(values)
        html.append(ol)
        ul = HtmlList(values, ordered=False)
        html.append(ul)
        text = HtmlText('this is some text\nwith a carriage return\nin several places')
        red = Font(color='red')
        text.font = red
        red.size = 1
        red.face = 'verdana'
        ol.html_items.append(copy.deepcopy(text))
        html.append(ol)
        text.paragraph = True
        text.font.color = 'blue'
        html.append(copy.deepcopy(text))
        text.font.size = None
        text.heading_level = 5
        html.append(copy.deepcopy(text))
        text.font.color = 'green'
        html.append(copy.deepcopy(text))
        headings = ['AAAA', 'BBBB', 'CCCC']
        data = [['a1', 'b1', 'c1'],
                ['a2', 'b2', 'c2'],
                ['a3', 'b3', 'c3'],
                ['a4', 'b4', 'c4'],
                ['a5', 'b5', 'c5']]
        table = HtmlTable(data=data, column_headings=headings)
        table.border = '1px solid #dddddd'
        table.text_align = 'center'
        #        table.padding = '8px'
        table.font_family = 'arial, sans-serif'
        table.border_collapse = 'collapse'
        table.width = '1000px'
        table.even_background_color = '#dddddd'
        table.odd_background_color = '#dddd00'
        html.append(table)
        image_file = os.path.join(os.path.join(pathlib.Path().parent.absolute().parent, 'attachments'), 'image_1.png')
        image = HtmlImage(image_file, height=100, width=120, alt_text='testing')
        html.append(HtmlLine())
        html.append(image)
        html.append(HtmlBreak())
        html.append(HtmlMailTo('jordan@thompco.com', 'Jordan Thompson'))
        html.append(HtmlBreak())
        html.append(HtmlCode('This is a test\nAnd another\nand another\nand yet another!'))
        the_file.write(html.to_string())
        the_file.close()
        os.system('python3 -m webbrowser -t "file://{}"'.format(os.path.join(pathlib.Path().absolute(), file_name)))


if __name__ == '__main__':
    main()
