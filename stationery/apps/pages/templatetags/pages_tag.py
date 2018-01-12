from django import template

from odinass.utils import format_price


register = template.Library()


@register.filter
def price(value):
    if value:
        return format_price(value)
