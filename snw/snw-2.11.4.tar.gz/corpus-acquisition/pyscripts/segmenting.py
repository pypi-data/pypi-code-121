import xml.etree.ElementTree as ET
import pcre

ns = {'srx20': 'http://www.lisa.org/srx20'}

class Segmenter(object):

    def __init__(self, srxfile, langcode, pure_srx=False, debug=False):
        tree = ET.parse(srxfile)
        root = tree.getroot()
        body = root.find('srx20:body', ns)
        self._lmap=[]
        rules=[]
        for child in body.find('srx20:maprules', ns).findall('srx20:languagemap', ns):
            if pcre.match(child.attrib["languagepattern"], langcode):
                self._lmap.append(child.attrib["languagerulename"])
        if debug:
            print("Matching languages:", ", ".join(self._lmap))
        for child in body.find('srx20:languagerules', ns).findall('srx20:languagerule', ns):
            if child.attrib["languagerulename"] in self._lmap:
                for rule in child.findall('srx20:rule', ns):
                    beforebreak=rule.find('srx20:beforebreak', ns)
                    if beforebreak is None or beforebreak.text is None:
                        beforebreak = ""
                    else:
                        beforebreak = beforebreak.text
                    afterbreak=rule.find('srx20:afterbreak', ns)
                    if afterbreak is None or afterbreak.text is None:
                        afterbreak = ""
                    else:
                        afterbreak = afterbreak.text
                    is_breaking=rule.attrib.get("break")=="yes"
                    regex = "("+beforebreak+")"+afterbreak
                    if pure_srx:
                        # Implement SRX regular expression definition
                        regex = regex.replace("\\s", "[\\t\\n\\f\\r\\p{Z}]")
                        regex = regex.replace("\\S", "[^\\t\\n\\f\\r\\p{Z}]")
                        regex = regex.replace("\\w", "[\\p{Ll}\\p{Lu}\\p{Lt}\\p{Lo}\\p{Nd}]")
                        regex = regex.replace("\\W", "[^\\p{Ll}\\p{Lu}\\p{Lt}\\p{Lo}\\p{Nd}]")
                    rules.append({"org": "  beforebreak: '%s'\n  afterbreak: '%s'" % (beforebreak, afterbreak),
                                  "re": pcre.compile(regex), "break": is_breaking})
        self._rules = rules
        self._debug = debug

    def get_langnames(self):
        return self._lmap

    def segment(self, text, trim=False):
        nobreakpos = {}
        breakpos = {}
        rid = 0
        for r in self._rules:
            rid += 1
            matches = r["re"].finditer(text)
            for m in matches:
                posbreak = m.start()+len(m.group(1))
                if self._debug:
                    print("Match [%s] in position %d-%d: \n%s"% (r["break"] and "break" or "nobreak", m.start(), posbreak, r["org"]))
                if posbreak not in breakpos and posbreak not in nobreakpos:
                    if r["break"]:
                        breakpos[posbreak]   = rid
                    else:   
                        nobreakpos[posbreak] = rid
        segments = []
        start_pos = 0
        for bp in sorted(breakpos.keys()):
            seq = text[start_pos:bp]
            if trim:
                seq = seq.strip()
            if len(seq):
                segments.append(seq)
            start_pos = bp
        seq = text[start_pos:]
        if trim:
            seq = seq.strip()
        if len(seq):
            segments.append(seq)
        return segments

