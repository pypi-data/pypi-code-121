from typing import Callable, Dict, Any, Tuple, List, Literal

from .baseui import BaseUi
from .output import Widget, Html

__all__ = ["Bootstrap", "NavLink", "Nav", "Icon", "Badge", "Pagination"]

COLOR = Literal[
    "primary" "secondary" "success" "danger" "warning" "info" "light" "dark"
]


class Bootstrap(BaseUi):
    def show(self):
        obj = self.widget.show()
        if hasattr(self, "style"):
            obj.style(self.style)
        if hasattr(self, "on_click"):
            obj.onclick(self.on_click)
        return obj

    def set_style(self, style):
        self.style = style

    def set_onclick(self, onclick):
        self.on_click = onclick


class NavLink(Bootstrap, Widget):
    template = """
    <a class="nav-link{{naactive}}" data-toggle="pill" role="tab" aria-controls="v-pills-profile" aria-selected="{{active}}">{{name}}</a>
    """

    def __init__(self, name: str, active: bool = False):
        self.name = name
        self.active = str(active).lower()
        self.widget = Widget(self.template, {"name": self.name, "active": self.active, 'naactive': ' active' if active else ''})


class Nav(Bootstrap, Widget):
    template = """
    <div class="nav flex-column nav-pills" role="tablist" aria-orientation="vertical">
    {{#menus}}
    {{& pywebio_output_parse}}
    {{/menus}}
    </div>
    """

    def __init__(self, menus: List[NavLink]):
        self.menus = menus
        self.data = {}

    def show(self):
        self.data = {"menus": list(map(self.ui_to_show, self.menus))}
        return Widget(self.template, self.data).show()


class Icon(Bootstrap):

    template = '<i class="bi {icon}"></i>'

    def __init__(self, icon: str):
        self.icon = icon
        self.htmls = Html(self.template.format(icon=self.icon))
    
    def show(self):
        return self.htmls.show()


class Badge(Bootstrap, Widget):

    template = """<span class="badge badge-{{color}}">{{text}}</span>"""

    def __init__(self, text: str, color: COLOR = "primary"):
        self.text = text
        self.color = color
        self.widget = Widget(self.template, {"text": self.text, "color": self.color})


class Pagination(Bootstrap, Widget):

    template = """
    <nav aria-label="Page navigation example">
    <ul class="pagination">
    <li class="page-item">
    <a class="page-link" href="#" aria-label="Previous">
    <span aria-hidden="true">&laquo;</span>
    </a>
    </li>
    <li class="page-item"><a class="page-link" href="#">1</a></li>
    <li class="page-item"><a class="page-link" href="#">2</a></li>
    <li class="page-item"><a class="page-link" href="#">3</a></li>
    <li class="page-item">
    <a class="page-link" href="#" aria-label="Next">
    <span aria-hidden="true">&raquo;</span>
    </a>
    </li>
    </ul>
    </nav>"""

    def __init__(self):
        self.widget = Widget(self.template)
