import Famcy
import json

class tbody(Famcy.FamcyElement):
    def __init__(self):
        super(tbody, self).__init__()

    def render_element(self):
        html = ""

        if self.innerHTML and self.innerHTML != "":
            html += self.innerHTML
            self.children = []
        else:
            for child in self.children:
                html += child.render_inner()
                child.parentElement = self
        self.html = html
        return "<tbody" + self.setAttrTag() + ">" + html + "</tbody>"