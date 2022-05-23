from django.template import Library, Node
import math

register = Library()

@register.simple_tag
def rest_of_division(a, b):
    return a % b

@register.simple_tag
def division(a, b):
    return a / b

@register.simple_tag
def ceil_division(a, b):
    return math.ceil(a / b)

@register.simple_tag
def sum(a, b):
    return int(a) + int(b)

@register.simple_tag
def trange(*args):
    return range(*args)

@register.simple_tag
def subtract(a , b):
    return a - b
