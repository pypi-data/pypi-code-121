import re
from unicodedata import normalize
from email_validator import validate_email, EmailNotValidError


class Cleansing(object):
    class Normalize:
        def __init__(self, string):
            self.string = string

        def execute(self):
            try:
                rem = normalize('NFKD', self.string) \
                    .encode('ASCII', 'ignore') \
                    .decode('ASCII')
                return rem

            except ValueError as e:
                pass

    class Prepositions:
        def __init__(self, string, prepositions):
            self.string = string
            self.prepositions = prepositions

        def execute(self):
            try:
                ajust_name = (' '.join(word if word in self.prepositions else word.title()
                                       for word in self.string.capitalize().split(' ')))
                return ajust_name

            except ValueError as e:
                pass

    class Phone:
        def __init__(self, string):
            self.string = string

        def phone_cleansing(self):
            number_pattern = re.compile('\\d')

            try:
                number = re.sub(number_pattern, '', self.string)
                x = len(self.string)

                if x < 8:
                    self.string = None

                elif x > 11:
                    self.string = number[x - 11:]

                return self.string

            except Exception as e:
                raise Exception(str(e))

        def phone_validate(self):
            fixed_pattern = re.compile('(\\d{3})?(\\d{2})?(\\d{4})(\\d{4})')
            mobile_pattern = re.compile('(\\d{3})?(\\d{2})?(\\d{5})(\\d{4})')

            try:
                phone_number = self.phone_cleansing()

                x = len(str(phone_number))

                if x == 8 or x == 10:
                    re.match(fixed_pattern, phone_number).group(0)

                    return 'Phone'

                elif x == 9 or x == 11:
                    re.match(mobile_pattern, phone_number).group(0)

                    return 'Mobile'

                else:
                    return 'Invalid'

            except Exception as e:
                raise Exception(str(e))

    class EMail:
        def __init__(self, string):
            self.string = string

        def email_validate(self):
            if self.string is not None:
                try:
                    validate_email(self.string)

                    return True

                except EmailNotValidError as e:
                    print(str(e))

                    return False

    class ClobDecoder:
        def __init__(self, string):
            self.string = string

        def parse(self):
            pattern = re.compile(r'\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)',
                                 re.I)

            destinations = frozenset((
                'aftncn', 'aftnsep', 'aftnsepc', 'annotation', 'atnauthor', 'atndate', 'atnicn', 'atnid',
                'atnparent', 'atnref', 'atntime', 'atrfend', 'atrfstart', 'author', 'background',
                'bkmkend', 'bkmkstart', 'blipuid', 'buptim', 'category', 'colorschememapping',
                'colortbl', 'comment', 'company', 'creatim', 'datafield', 'datastore', 'defchp', 'defpap',
                'do', 'doccomm', 'docvar', 'dptxbxtext', 'ebcend', 'ebcstart', 'factoidname', 'falt',
                'fchars', 'ffdeftext', 'ffentrymcr', 'ffexitmcr', 'ffformat', 'ffhelptext', 'ffl',
                'ffname', 'ffstattext', 'field', 'file', 'filetbl', 'fldinst', 'fldrslt', 'fldtype',
                'fname', 'fontemb', 'fontfile', 'fonttbl', 'footer', 'footerf', 'footerl', 'footerr',
                'footnote', 'formfield', 'ftncn', 'ftnsep', 'ftnsepc', 'g', 'generator', 'gridtbl',
                'header', 'headerf', 'headerl', 'headerr', 'hl', 'hlfr', 'hlinkbase', 'hlloc', 'hlsrc',
                'hsv', 'htmltag', 'info', 'keycode', 'keywords', 'latentstyles', 'lchars', 'levelnumbers',
                'leveltext', 'lfolevel', 'linkval', 'list', 'listlevel', 'listname', 'listoverride',
                'listoverridetable', 'listpicture', 'liststylename', 'listtable', 'listtext',
                'lsdlockedexcept', 'macc', 'maccPr', 'mailmerge', 'maln', 'malnScr', 'manager', 'margPr',
                'mbar', 'mbarPr', 'mbaseJc', 'mbegChr', 'mborderBox', 'mborderBoxPr', 'mbox', 'mboxPr',
                'mchr', 'mcount', 'mctrlPr', 'md', 'mdeg', 'mdegHide', 'mden', 'mdiff', 'mdPr', 'me',
                'mendChr', 'meqArr', 'meqArrPr', 'mf', 'mfName', 'mfPr', 'mfunc', 'mfuncPr', 'mgroupChr',
                'mgroupChrPr', 'mgrow', 'mhideBot', 'mhideLeft', 'mhideRight', 'mhideTop', 'mhtmltag',
                'mlim', 'mlimloc', 'mlimlow', 'mlimlowPr', 'mlimupp', 'mlimuppPr', 'mm', 'mmaddfieldname',
                'mmath', 'mmathPict', 'mmathPr', 'mmaxdist', 'mmc', 'mmcJc', 'mmconnectstr',
                'mmconnectstrdata', 'mmcPr', 'mmcs', 'mmdatasource', 'mmheadersource', 'mmmailsubject',
                'mmodso', 'mmodsofilter', 'mmodsofldmpdata', 'mmodsomappedname', 'mmodsoname',
                'mmodsorecipdata', 'mmodsosort', 'mmodsosrc', 'mmodsotable', 'mmodsoudl',
                'mmodsoudldata', 'mmodsouniquetag', 'mmPr', 'mmquery', 'mmr', 'mnary', 'mnaryPr',
                'mnoBreak', 'mnum', 'mobjDist', 'moMath', 'moMathPara', 'moMathParaPr', 'mopEmu',
                'mphant', 'mphantPr', 'mplcHide', 'mpos', 'mr', 'mrad', 'mradPr', 'mrPr', 'msepChr',
                'mshow', 'mshp', 'msPre', 'msPrePr', 'msSub', 'msSubPr', 'msSubSup', 'msSubSupPr', 'msSup',
                'msSupPr', 'mstrikeBLTR', 'mstrikeH', 'mstrikeTLBR', 'mstrikeV', 'msub', 'msubHide',
                'msup', 'msupHide', 'mtransp', 'mtype', 'mvertJc', 'mvfmf', 'mvfml', 'mvtof', 'mvtol',
                'mzeroAsc', 'mzeroDesc', 'mzeroWid', 'nesttableprops', 'nextfile', 'nonesttables',
                'objalias', 'objclass', 'objdata', 'object', 'objname', 'objsect', 'objtime', 'oldcprops',
                'oldpprops', 'oldsprops', 'oldtprops', 'oleclsid', 'operator', 'panose', 'password',
                'passwordhash', 'pgp', 'pgptbl', 'picprop', 'pict', 'pn', 'pnseclvl', 'pntext', 'pntxta',
                'pntxtb', 'printim', 'private', 'propname', 'protend', 'protstart', 'protusertbl', 'pxe',
                'result', 'revtbl', 'revtim', 'rsidtbl', 'rxe', 'shp', 'shpgrp', 'shpinst',
                'shppict', 'shprslt', 'shptxt', 'sn', 'sp', 'staticval', 'stylesheet', 'subject', 'sv',
                'svb', 'tc', 'template', 'themedata', 'title', 'txe', 'ud', 'upr', 'userprops',
                'wgrffmtfilter', 'windowcaption', 'writereservation', 'writereservhash', 'xe', 'xform',
                'xmlattrname', 'xmlattrvalue', 'xmlclose', 'xmlname', 'xmlnstbl',
                'xmlopen',
            ))

            special_chars = {
                'par': '\n',
                'sect': '\n\n',
                'page': '\n\n',
                'line': '\n',
                'tab': '\t',
                'emdash': '\u2014',
                'endash': '\u2013',
                'emspace': '\u2003',
                'enspace': '\u2002',
                'qmspace': '\u2005',
                'bullet': '\u2022',
                'lquote': '\u2018',
                'rquote': '\u2019',
                'ldblquote': '\201C',
                'rdblquote': '\u201D',
            }

            stack = []
            ignorable = False
            uc_skip = 1
            cur_skip = 0
            out = []

            for match in pattern.finditer(self.string):
                word, arg, hex_char, char, brace, temp_char = match.groups()

                if brace:
                    cur_skip = 0

                    if brace == '{':
                        stack.append((uc_skip, ignorable))

                    elif brace == '}':
                        uc_skip, ignorable = stack.pop()

                elif char:
                    cur_skip = 0

                    if char == '~':
                        if not ignorable:
                            out.append('\xA0')

                    elif char in '{}\\':
                        if not ignorable:
                            out.append(char)

                    elif char == '*':
                        ignorable = True

                elif word:
                    cur_skip = 0

                    if word in destinations:
                        ignorable = True

                    elif ignorable:
                        pass

                    elif word in special_chars:
                        out.append(special_chars[word])

                    elif word == 'uc':
                        uc_skip = int(arg)

                    elif word == 'u':
                        c = int(arg)

                        if c < 0:
                            c += 0x10000
                            
                        if c > 127:
                            out.append(chr(c))

                        else:
                            out.append(chr(c))

                        cur_skip = uc_skip

                elif hex_char:
                    if cur_skip > 0:
                        cur_skip -= 1

                    elif not ignorable:
                        c = int(hex_char, 16)

                        if c > 127:
                            out.append(chr(c))

                        else:
                            out.append(chr(c))

                elif temp_char:
                    if cur_skip > 0:
                        cur_skip -= 1

                    elif not ignorable:
                        out.append(temp_char)

            return ''.join(out)
