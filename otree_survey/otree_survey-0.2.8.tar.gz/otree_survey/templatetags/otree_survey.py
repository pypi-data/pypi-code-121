from django import template
from django.utils.translation import ugettext_lazy as _
from otree.templatetags.otree_forms import FormFieldNode

register = template.Library()


@register.inclusion_tag("otree_survey/tags/BackButton.html", takes_context=True)
def back_button(context, *args, **kwargs):
    if "show_back" not in context:
        raise Exception(
            r"use SurveyPage as the super class for views that use the {% back %} button"
        )
    return context


@register.inclusion_tag("otree_survey/tags/NavigationButtons.html", takes_context=True)
def navigation_buttons(context, *args, **kwargs):
    if "show_back" not in context:
        raise Exception(
            r"use SurveyPage as the super class for views that use the {% back %} button"
        )
    context["show_next"] = context.get("show_next", True)
    context["next_text"] = context.get("next_text", _("Next"))
    context["back_text"] = context.get("back_text", _("Back"))
    return context


@register.inclusion_tag("otree_survey/tags/ProgressBar.html", takes_context=True)
def progress_bar(context, *args, **kwargs):
    return context


@register.inclusion_tag("otree_survey/tags/FormfieldOnly.html")
def formfieldonly(field, *args, **kwargs):
    return {"field": field}


@register.inclusion_tag("otree_survey/tags/LikertFields.html")
def likert_fields(form, fields=None, *args, **kwargs):
    return {"form": form, "fields": fields}


# customize the otree FormField template, to fix layout of MultipleChoiceStringField
FormFieldNode.template_name = "otree_survey/tags/Formfield.html"
