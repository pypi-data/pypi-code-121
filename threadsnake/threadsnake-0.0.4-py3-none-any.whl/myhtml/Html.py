##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com

from functools import reduce
from typing import Dict, List, Tuple

class HtmlNode:
    def render(self, tabLevel:int = 0):
        pass

class HtmlText(HtmlNode):
    def __init__(self, content:str = ''):
        super().__init__()
        self.content = content
    
    def render(self, tabLevel: int = 0):
        return '\t'*tabLevel + f'{self.content}'

class HtmlElement(HtmlNode):
    def __init__(self, tagName:str, attributes:Dict[str, str] = None, children:List[HtmlNode] = None):
        self.tagName = tagName
        self.attributes = attributes or dict()
        self.children = children or []
        
    def __getitem__(self, index):
        res = []
        for i in self.children:
            if not isinstance(i, HtmlElement):
                print('nothtml')
                continue
            if isinstance(index, int) and len(self.children) > index:
                res = [self.children[index]]
                break
            if not isinstance(index, str):
                raise Exception("Name should be int or string")
            if index.startswith('.') and 'class' in i.attributes and index[1:] in i.attributes['class'].split(' '):
                res.append(i)
            elif index.startswith('#') and 'id' in i.attributes and i.attributes['id'] == index[1:]:
                res.append(i)
            elif i.tagName == index:
                res.append(i)
        return res
    
    def for_each(self, selector, action):
        for c in self[selector]:
            action(c)
    
    def render(self, tabLevel:int = 0):
        result = tabLevel * '\t' + f'<{self.tagName}'
        if(len(self.attributes) == 0 and len(self.children) == 0):
            result += '/>\n'
        else:
            if len(self.attributes) > 0:
                result += reduce(lambda a, b: a+b, [f' {i}="{self.attributes[i]}"' for i in self.attributes])
            result += '>\n'
            for c in self.children:
                result += c.render(tabLevel + 1)
            result += tabLevel * '\t' + f'</{self.tagName}>\n'
        return result
    
    def append_child(self, *children:HtmlNode):
        for child in children:
            self.children.append(child)
        return self

    def set_attribute(self, attributeName:str, attributeValue:str):
        self.attributes[attributeName] = attributeValue
        return self
    
def script(src:str):
    return HtmlElement('script', {'src':src})
    
def style(href:str):
    return HtmlElement('link', {'rel':'stylesheet','href':href})
    
def head(title:str, scripts:List[str] = [], styles:List[str] = []):
    result = HtmlElement('head', children=[text_element(title, 'title')])
    for stl in styles:
        result.append_child(style(stl))
    for scr in scripts:
        result.append_child(script(scr))
    return result

def link(text:str, href:str):
    return HtmlElement('a', {'href':href}).append_child(HtmlText(text))

def text_element(text:str, tag:str = 'div', attributes:Dict[str, str] = None):
    return HtmlElement(tag, attributes or dict()).append_child(HtmlText(text))

def html(title:str):
    result = HtmlElement('html').append_child(head(title))
    result.append_child(HtmlElement('body', children=[link('google', 'www.google.com')]))
    return result

def page(title:str, scripts:List[str] = [], styles:List[str] = []) -> Tuple[HtmlElement, HtmlElement]:
    content = HtmlElement('div', {"class":"mainContent"})
    html = HtmlElement('html').append_child(head(title, scripts, styles))
    html.append_child(HtmlElement('body', children=[content]))
    return html, content

def header(title:str):
    return text_element(title, 'header')

def nodes_group(tag:str, *children:HtmlNode):
    result = HtmlElement(tag)
    for c in children:
        result.append_child(c)
    return result

def links_group(tag:str, links:Dict[str, str] = dict()):
    result = HtmlElement(tag)
    for l in links:
        result.append_child(link(l, links[l]))
    return result

def nav(links:Dict[str, str] = dict()):
    return links_group('nav', links)

def aside(links:Dict[str, str] = dict()):
    return links_group('aside', links)