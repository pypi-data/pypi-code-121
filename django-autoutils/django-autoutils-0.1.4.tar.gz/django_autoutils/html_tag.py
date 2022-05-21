import json

from django.urls import reverse, NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer


def get_edit_url(instance):
    try:
        # noinspection PyProtectedMember
        return reverse(f'admin:{instance._meta.app_label}_{instance._meta.model_name}_change', args=[instance.pk])
    except NoReverseMatch:
        return ''


def get_link(url, text, title=""):
    return format_html(f'<a href={url} title={title}>{text}</a>')


def get_error_link(url, text, title=""):
    return format_html(f'<a href={url} title={title} style="color:red;" target="_blank">{text}</a>')


def get_button_link(url, text, title=""):
    return format_html(f'<a href={url} class="button" title="{title}" target="_blank">{text}</a>')


def get_pretty_json(data):
    """Function to display pretty version of our data"""

    # Convert the data to sorted, indented JSON
    response = json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False)

    # Truncate the data. Alter as needed
    response = response[:5000]

    # Get the Pygments formatter
    formatter = HtmlFormatter(style='colorful')

    # Highlight the data
    response = highlight(response, JsonLexer(), formatter)
    # Get the stylesheet
    style = "<style>" + formatter.get_style_defs() + "</style><br>"

    # Safe the output
    return mark_safe(style + response)


def get_image_link(image, width, height, border_radius, title="image", link=""):
    return format_html(
        f'<a href={link}>'
        f'<image src="{image}" width="{width}" height="{height}" '
        f'title="{title}" style="border-radius: {border_radius}%"/>'
        f'</a>')


def get_image_text(image, width, height, border_radius, text):
    return format_html(
        f'<div>'
        f'<image src="{image}" width="{width}" height="{height}" '
        f'title="{text}" style="border-radius: {border_radius}%"/>'
        f'{text}'
        f'</div>')


def get_avatar_icon(image, title="icon", link=""):
    if not image:
        return None
    return get_image_link(image.url, width=30, height=30, border_radius=50, title=title, link=link)


def get_avatar_image(image, title="image", link=""):
    if not image:
        return None
    return get_image_link(image.url, width=150, height=150, border_radius=20, title=title, link=link)


def get_edit_icon(instance, image_field="avatar", title=None):
    if not instance.pk:
        return ''
    if title is None:
        title = str(instance)
    return get_avatar_icon(getattr(instance, image_field, None), title=title, link=get_edit_url(instance))


def get_edit_link(instance, text=_("edit"), title=_("click for edit object")):
    if not instance.pk:
        return ''
    return get_link(get_edit_url(instance), text, title=title)


def get_error_edit_link(instance, text=_("edit"), title=_("click for show object")):
    if not instance.pk:
        return ''
    return get_error_link(get_edit_url(instance), text, title=title)


def get_user_icon(user, title="", link=""):
    if not user:
        return None
    icon = None
    if user.avatar:
        icon = get_avatar_icon(user.avatar, title=title, link=link)
    edit_url = get_edit_link(user, f"{user}")
    return format_html(
        f'<div title={title}>'
        f'{icon}'
        f'</br>'
        f'{edit_url}'
        f'</div>'
    )
