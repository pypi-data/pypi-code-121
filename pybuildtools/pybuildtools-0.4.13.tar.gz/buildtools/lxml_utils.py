'''
lxml Utility Functions

Copyright (c) 2015 - 2022 Rob "N3X15" Nelson <nexisentertainment@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''
from lxml import etree


def stripNS(tagName):
    i = tagName.find('}')
    if i >= 0:
        tagName = tagName[i + 1:]
    return tagName


def getText(element):
    if element is None:
        return None
    return element.text


def copyAttribute(kwargs, argname, element, default=None):
    value = kwargs.get(argname, default)
    if value is not None:
        element.set(argname, value)


def e(name, attr={}, children=[]):
    el = etree.Element(name)
    for k, v in attr.items():
        el[k] = v
    for c in children:
        if isinstance(c, str):
            el.text = c
            break
        el.append(c)
    return el
