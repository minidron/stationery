from django import template

from odinass.utils import format_price


register = template.Library()


@register.filter
def price(value):
    if value:
        price = '%s руб' % format_price(value)
    else:
        price = 'Нет цены'
    return price
