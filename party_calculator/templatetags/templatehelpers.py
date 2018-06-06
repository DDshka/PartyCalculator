from django import template

register = template.Library()


@register.filter('mul')
def mul(a, b):
    if a is None or b is None:
        return None

    return a * b


@register.filter('div')
def div(a, b):
    if a is None or b is None:
        return None

    return a / b
