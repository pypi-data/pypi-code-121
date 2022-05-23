from django import template

register = template.Library()

@register.simple_tag
def truncatesmart(value, limit=80, suffix="..."):
    """
    Truncates a string after a given number of chars keeping whole words.

    Usage:
        {% truncatesmart string }}
        {% truncatesmart string limit=50 }}
    """
    try:
        limit = int(limit)
    # invalid literal for int()
    except ValueError:
        # Fail silently.
        return value

    # Return the string itself if length is smaller or equal to the limit
    if len(value) <= limit:
        return value

    # Break into words and remove the last
    words = value.split(' ')

    current_count = 0
    index = 0

    while (current_count + len(words[index])) < limit:
        current_count += len(words[index])
        if current_count + 1 < limit:
            current_count += 1
        index += 1

    # Join the words and return
    return ' '.join(words[:index]) + suffix
