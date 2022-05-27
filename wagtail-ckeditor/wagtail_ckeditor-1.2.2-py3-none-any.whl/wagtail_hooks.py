from wagtail.admin.rich_text.converters.editor_html import WhitelistRule
from wagtail.core import hooks
from wagtail.core.whitelist import allow_without_attributes, attribute_rule


@hooks.register("register_rich_text_features")
def apply_whitelist(features):
    features.register_converter_rule(
        "editorhtml",
        "ckeditor_features",
        [
            WhitelistRule("s", allow_without_attributes),
            WhitelistRule("u", allow_without_attributes),
            WhitelistRule(
                "span", attribute_rule({"style": True, "class": True})
            ),
            WhitelistRule("p", attribute_rule({"style": True, "class": True})),
            WhitelistRule(
                "div", attribute_rule({"style": True, "class": True})
            ),
            WhitelistRule("q", allow_without_attributes),
            WhitelistRule("ins", allow_without_attributes),
            WhitelistRule("pre", allow_without_attributes),
            WhitelistRule(
                "addres",
                attribute_rule(
                    {
                        "class": True,
                        "href": True,
                        "data-toggle": True,
                        "style": True,
                    }
                ),
            ),
            WhitelistRule(
                "a",
                attribute_rule(
                    {
                        "class": True,
                        "href": True,
                        "data-toggle": True,
                        "style": True,
                    }
                ),
            ),
            WhitelistRule(
                "div",
                attribute_rule(
                    {
                        "align": True,
                        "border": True,
                        "cellpadding": True,
                        "style": True,
                    }
                ),
            ),
            WhitelistRule("caption", allow_without_attributes),
            WhitelistRule("thead", allow_without_attributes),
            WhitelistRule("tr", allow_without_attributes),
            WhitelistRule("tbody", allow_without_attributes),
            WhitelistRule(
                "td", attribute_rule({"style": True, "class": True})
            ),
            WhitelistRule("hr", allow_without_attributes),
            WhitelistRule(
                "img",
                attribute_rule(
                    {
                        "alt": True,
                        "src": True,
                        "style": True,
                        "width": True,
                        "height": True,
                    }
                ),
            ),
        ],
    )
    features.default_features.append("ckeditor_features")
