from chilitools.utilities.errors import ErrorHandler
from xml.etree.ElementTree import Element, SubElement, tostring
import re

illegalXMLCharacters = re.compile(u'[\x00-\x08\x0b\x0c\x0e-\x1F\uD800-\uDFFF\uFFFE\uFFFF]')

def unescapeXML(xml: str) -> str:
    from xml.sax.saxutils import unescape
    return unescape(xml)

def parseXML(xml: str):
    import xmltodict
    return xmltodict.parse(xml)

def cleanXML(val, replacement='') -> str:
    return illegalXMLCharacters.sub(replacement, val)

def sanitize_text(data):
    replace_with = {
        u'\u2018': '\'',
        u'\u2019': '\'',
        u'\u201c': '"',
        u'\u201d': '"'
    }

    bad_chars = [c for c in data if ord(c) >= 127]
    if bad_chars:
        print('INVALID CHARACTERS: {}'.format(bad_chars))
    else:
        print('INVALID CHARACTERS: {}'.format(bad_chars))

    for uni_char in replace_with.keys():
        data = data.replace(uni_char, replace_with.get(uni_char))

    data = ''.join([c for c in data if ord(c) < 127])
    return data.encode('utf-8', 'xmlcharreplace')

def createDatasourceXML(dataSourceID: str, data: list[dict]) -> str:
    numChildren = len(data)
    root = Element('dataSource', {'dataSourceID':dataSourceID, 'hasContent':'true', 'numRows':str(numChildren)})
    for r in range(numChildren):
        row = SubElement(root, 'row', {'rowNum':str(r+1)})
        c = 1
        for key, value in data[r].items():
            col = SubElement(row, 'col'+str(c), {'varName':key})
            col.text = str(value)
            c += 1
    return tostring(root, encoding='unicode')

def taskWasSuccessfull(task) -> bool:
    if task['task']['@succeeded'] == "True":
        return True
    return False

def getTaskResultURL(task) -> str:
    if taskWasSuccessfull(task=task):
        result = task['task']['@result']
        result = unescapeXML(result)
        result = parseXML(result)
        return result['result']['@url']
    return ErrorHandler().getError(errorName="TASKNOTSUCCEEDED")