from django.utils.safestring import mark_safe
from django.template.defaulttags import register


@register.simple_tag()
def eve_logo(id, name, cat, size):
    if cat == "character":
        return mark_safe("<img class=\"img-circle\" src=\"https://images.evetech.net/characters/%s/portrait?size=%s\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    elif cat == "corporation":
        return mark_safe("<img class=\"img-circle\" src=\"https://images.evetech.net/corporations/%s/logo?size=%s\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    elif cat == "alliance":
        return mark_safe("<img class=\"img-circle\" src=\"https://images.evetech.net/alliances/%s/logo?size=%s\" style=\"height: %spx; width: %spx;\" title=\"%s\">" % (id, size, size, size, name))

    else:
        return ""
