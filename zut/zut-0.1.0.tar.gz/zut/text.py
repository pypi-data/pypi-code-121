import re, unicodedata

def slugify(value: str, allow_unicode=False, separator='-', discard_underscores=False, specials=False):
    """
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    #NOTE: this is an extension of "slugify" function in django.zut.text 
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )

    value = value.lower()

    if specials:
        # french special: replace "l'" and "d'" to ensure hyphen will be kept
        value = value.replace("l'", "l-").replace("d'", "d-")
    
    value = re.sub(r"[^\w\s" + separator + r"]", "", value)
    return re.sub(r"[" + separator + (r"_" if discard_underscores else "") + r"\s]+", separator, value).strip(separator + "_")


def safe_slugify(value: str, allow_unicode=False, separator='-', preserve='', discard_underscores=True, custom_slugs=None):
    if value is None:
        return None
    
    if custom_slugs and value in custom_slugs:
        return custom_slugs[value]

    if preserve:
        values = value.split(preserve)
    else:
        values = [value]

    slugs = []
    for value in values:
        slug = slugify(value, allow_unicode=allow_unicode, separator=separator, discard_underscores=discard_underscores, specials=True)
        slugs.append(slug)
    
    return preserve.join(slugs)
