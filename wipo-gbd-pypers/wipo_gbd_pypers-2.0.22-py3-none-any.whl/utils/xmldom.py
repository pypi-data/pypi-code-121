import os
import codecs
import re
import lxml.etree as ET
from xml.dom.minidom import parse


def get_ns_from_xml(xml_file):
    regex = re.compile(
        r"xmlns=\"((http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?)\"",
        re.IGNORECASE)
    ns = ''
    with open(xml_file, 'r') as f:
        counter = 0
        while counter < 10:
            line = f.readline()
            if 'xmlns' in line:
                ns = re.findall(regex, line)[0][0]
                break
            counter += 1
    return ns

def remove_doctype(file):
    filef = '%s.clean' % file

    with open(file, 'r') as fh:
        lines = fh.readlines()
        lines = [line.rstrip() for line in lines]

    with open(filef, 'w') as fh:
        for line in lines:
            if line.startswith('<!DOCTYPE'):
                pass
            else:
                fh.write('%s\n' % line)

    os.remove(file)
    os.rename(filef, file)
    return file


def clean_xmlfile(file, overwrite=False, readenc='utf8',
                  writeenc='utf8', chars=(), ordinals=()):
    filef = '%s.clean' % file

    # has been cleaned. do not duplicate work
    if os.path.exists(filef):
        return filef

    lines = []

    with codecs.open(file, 'rb', readenc, errors='ignore') as inf:
        for line in inf:
            # remove embedded line breaks
            line = line.replace('\r', '').replace('\n', ' ').rstrip()
            # remove control characters
            line = ''.join(c for c in line if (ord(c) >= 32))
            # and ord(c) <= 927))
            # yes it happens, the replace should be smarter though.
            line = line.replace('& ', '&amp; ')
            # remove illegal entity
            line = line.replace('&#x1C;', '')

            for char, replace in chars:
                line = line.replace(char, replace)

            if len(ordinals) > 0:
                lchars = [c for c in line]
                for ordinal, replace in ordinals:
                    for i, c in enumerate(lchars):
                        if ord(c) == ordinal:
                            lchars[i] = replace
                line = ''.join(lchars)

            lines.append(line)

    if len(lines):
        with codecs.open(filef, 'wb', writeenc) as fixed:
            fixed.write('\n'.join(lines))

        if overwrite:
            os.remove(file)
            os.rename(filef, file)
            return file
        else:
            return filef
    else:
        raise Exception('[%s] empty file. Nothing to clean!' % file)


def get_nodevalue(nodename, file=None, dom=None, ns='*'):
    if not file and dom is None:
        raise Exception('get_nodevalue of what? neither file nor dom is passed')

    try:
        if file:
            dom = parse(file)
    except Exception as e:
        raise Exception('[%s] corrupt XML file. could not be parsed.' %
                        os.path.basename(file))

    try:
        matches = dom.getElementsByTagNameNS(ns, nodename)
        if not len(matches):
            return ''
        else:
            match = matches[0]
            return str(match.firstChild.nodeValue)
    except Exception as e:
        return ''


def set_nodevalue(nodename, nodevalue, force=False, file=None,
                  dom=None, ns='*'):
    if not file and not dom:
        raise Exception('set_nodevalue of what? neither file nor dom is passed')
    try:
        if file:
            dom = parse(file)

        matches = dom.getElementsByTagNameNS(ns, nodename)
        if not len(matches):
            if force:
                newelt = dom.createElement(nodename)
                newelt_val = dom.createTextNode(str(nodevalue))
                newelt.appendChild(newelt_val)
                dom.childNodes[0].appendChild(newelt)
                if file:
                    save_xml(dom, file)
            if file:
                return file
            else:
                return dom
        else:
            match = matches[0]
            match.firstChild.replaceWholeText(nodevalue)

            if file:
                save_xml(dom, file)
                return file
            else:
                return dom
    except Exception as e:
        return None


def get_nodevalues(nodename, file=None, dom=None, ns='*'):
    if not file and not dom:
        raise Exception('get_nodevalue of what? neither file nor dom is passed')

    values = []

    try:
        if file:
            dom = parse(file)
        matches = dom.getElementsByTagNameNS(ns, nodename)
        if not len(matches):
            return values
        else:
            for match in matches:
                values.append(str(match.firstChild.nodeValue))

            return values
    except Exception as e:
        return values


def transform(xml, xsl, file):
    dom = ET.parse(xml)
    xslt = ET.parse(xsl)
    newdom = ET.XSLT(xslt)(dom)

    with open(file, 'wb') as fh:
        fh.write(ET.tostring(newdom, pretty_print=True))


def create_element(file, nodename, nodevalue):
    dom = parse(file)
    elt = dom.createElement(nodename)
    elt_text = dom.createTextNode(nodevalue)
    elt.appendChild(elt_text)

    dom.childNodes[0].appendChild(elt)

    save_xml(dom, file)


def save_xml(dom, file, indent='', addindent='', newl='', enc='UTF-8'):
    with codecs.open(file, 'wb', enc) as fh:
        dom.writexml(fh, indent=indent,
                         addindent=addindent,
                         newl=newl,
                         encoding=enc)
