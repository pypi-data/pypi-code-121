# html_writer.py: class to write HTML reports (with console colors)
from xtlib import pc_utils

ESCAPE_CHAR = "\033"

class HtmlWriter():
    def __init__(self, simple) -> None:
        self.in_span = False
        self.simple = simple

        if simple:
            # use black on white bg
            fg_color = "black"   
            bg_color = "white"  
        else:
            # use white on black bg
            fg_color = "#f2f2f2"   # almost white
            bg_color = "#0c0c0c"    # almost black

        font_size = "16.3px"

        self.prefix_template = 'Version:0.9\r\n' \
            'StartHTML:0000000105\r\nEndHTML:{:010d}\r\n'  \
            'StartFragment:0000000141\r\nEndFragment:{:010d}\r\n' \
            '<html>\r\n' \
            '<body>\r\n<!--StartFragment--><div style="color: ' + fg_color + ';' \
            'background-color: ' + bg_color + ';font-family: Consolas, \'Courier New\',' \
            'monospace;font-weight: normal;font-size: ' + font_size + ';line-height: 19px;' \
            'white-space: pre;">' \
            '<div>'

        self.suffix = b'</div></div><!--EndFragment-->\r\n</body>\r\n</html>\x00'

        self.colors = pc_utils.COLORS + pc_utils.LIGHT_COLORS
        self.build_html_color_dict()

    def build_html_color_dict(self):
        self.html_color_dict = {
            pc_utils.BLACK: "darkgray", pc_utils.RED: "red", pc_utils.GREEN: "green", pc_utils.YELLOW: "yellow",
            pc_utils.BLUE: "#569cd6", pc_utils.MAGENTA: "#b4009e", pc_utils.CYAN: "cyan", pc_utils.GRAY: "gray", 

            pc_utils.LIGHTRED: "red", pc_utils.LIGHTGREEN: "lightgreen", pc_utils.LIGHTYELLOW: "yellow",
            pc_utils.LIGHTBLUE: "lightblue", pc_utils.LIGHTMAGENTA: "magenta", pc_utils.LIGHTCYAN: "cyan",
            pc_utils.DARKGRAY: "darkgray", pc_utils.WHITE: "white",
        }

    def html_for_escape(self, text, index):
        html = ""
        crlen = len(pc_utils.RED)
        assert text[index] == ESCAPE_CHAR

        escape3 = text[index:index+3]
        escape4 = text[index:index+4]
        escape6 = text[index:index+6]
        escape7 = text[index:index+7]

        if escape4 == pc_utils.NORMAL:
            if self.in_span:
                self.in_span = False
                html = "</span><break>"
            index += len(pc_utils.NORMAL)

        elif escape4 == pc_utils.BOLD:
            if self.in_span:
                self.in_span = False
                html = "</span>"
            html += "<span style='font-weight: bold;'>"
            self.in_span = True
            index += len(pc_utils.BOLD)

        elif escape7 in self.colors:
            if self.in_span:
                self.in_span = False
                html = "</span>"

            html_color = self.html_color_dict[escape7]
            if self.simple:
                # use BOLD in place of a color 
                # this is a workaround for all the issues with pasting HTML into OneNote
                html += "<span style='font-weight: bold;'>"
            else:
                # use specified color
                html += "<span style='color: {};'>".format(html_color)

            self.in_span = True
            index += crlen

        elif escape3 in [pc_utils.CLEAR_LINE, pc_utils.CURSOR_UP]:
            # ignore these
            index += 3

        elif escape6 in [pc_utils.UNDERLINE, pc_utils.NEGATIVE]:
            # ignore these
            index += 6

        elif escape7 in [pc_utils.NOUNDERLINE, pc_utils.POSITIVE]:
            # ignore these
            index += 7

        else:
            # unsupported ESCAPE code
            index += 3

        return html, index

    def process_escape_codes(self, text):
        start = 0
        new_text = ""

        while ESCAPE_CHAR in text[start:]:
            index = text.index(ESCAPE_CHAR, start)
            new_text += text[start:index]
            
            html, index = self.html_for_escape(text, index)
            new_text += html
            start = index

        # add remaining text not containing an escape char
        new_text += text[start:]

        return new_text

    def write(self, text):

        # fixup special chars for HTML
        text = text.replace("±", "&#177")
        #text = text.replace("\r", "")

        # convert console colors to HTML colors
        text = self.process_escape_codes(text)

        text = text.encode("LATIN-1")

        end_fragment = 331 + len(text)
        end_html = end_fragment + 36

        prefix = self.prefix_template.format(end_html, end_fragment).encode("LATIN-1")
        html = prefix + text + self.suffix

        # print("post-end-fragment", html[end_fragment:])
        # print("post-end-html", html[end_html:])
        return html

def test(text):
    from xtlib.helpers import clipboard 
    #print(text)

    writer = HtmlWriter()

    html = writer.write(text)

    # write html to clipboard
    with clipboard.Clipboard() as cb:
        cb.set_contents("HTML FORMAT", html)
        formats = cb.enum_formats()
        #print("enum_formats:", formats)
        value = cb.get_contents("HTML FORMAT")
        #print("test_get:", value)

def test_contents():
    from xtlib.helpers import clipboard 
    with clipboard.Clipboard() as cb:
        value = cb.get_contents("HTML FORMAT")
        print("test_get:", value)    

def test_from_clipboard():
    from xtlib.helpers import clipboard 
    with clipboard.Clipboard() as cb:
        console_text = cb.get_contents("CF_TEXT")
        writer = HtmlWriter()
        html = writer.write(console_text)
        cb.set_contents("HTML FORMAT", html)

if __name__ == "__main__":
    #test_contents()

    # test("Colors: {}black {}red {}green {}yellow {}blue {}magenta {}cyan {}gray".format(pc_utils.BLACK, pc_utils.RED,
    #     pc_utils.GREEN, pc_utils.YELLOW, pc_utils.BLUE, pc_utils.MAGENTA, pc_utils.CYAN, pc_utils.GRAY))

    # test("Lights: {}red {}green {}yellow {}blue {}magenta {}cyan {}dark gray {} white".
    #     format(pc_utils.LIGHTRED, pc_utils.LIGHTGREEN, pc_utils.LIGHTYELLOW, pc_utils.LIGHTBLUE, pc_utils.LIGHTMAGENTA, 
    #     pc_utils.LIGHTCYAN, pc_utils.DARKGRAY, pc_utils.WHITE))

    text = \
        "TASK: nc_pat/active_logical_ttb\n[1;35mRUNSET                 NUM_PARAMS  COUNT  BEST-EVAL-ACC  " \
        "  STEP    TRAIN-ACC    DEV-ACC      EVAL_NEW_ADJ-ACC  EVAL_LONG_ADJ-ACC[0m\n\n" \
        "  best_cogs_transformer  28,173,590      5  0.00 ± 0.00    30,000  1.00 ± 0.00  1.00 ± 0.00  0.30 ± 0.00       0.00 ± 0.00     \n"\
        "  poor_cogs_transformer  87,885,552      5  0.00 ± 0.00    30,000  0.29 ± 0.19  0.55 ± 0.25  0.24 ± 0.08       0.00 ± 0.00      \n"\
        "  default_transformer    44,198,912      5  0.00 ± 0.00    30,000  0.99 ± 0.00  1.00 ± 0.00  0.30 ± 0.00       0.00 ± 0.00      \n"\
        "  best_cogs_colette      2,572,688       5  0.00 ± 0.00    30,000  0.98 ± 0.00  1.00 ± 0.00  0.30 ± 0.00       0.00 ± 0.00   "

    test(text)