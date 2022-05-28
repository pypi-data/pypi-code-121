from html.parser import HTMLParser

class TagParser(HTMLParser):
    def __init__(self, searched_tag):
        super().__init__()
        self.searched_tag = searched_tag
        self.match = False
        self.data = None

    def handle_starttag(self, tag, attributes):
        self.match = tag == self.searched_tag

    def handle_data(self, data):
        if self.match:
            self.data = data
            self.match = False

def find_tag_content(html: str, tag: str):
    parser = TagParser(tag)
    parser.feed(html)
    return parser.data
