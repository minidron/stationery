from django import template

from odinass.utils import format_price


register = template.Library()


@register.filter
def price(value):
    if not value:
        return ''
    return format_price(value)


@register.simple_tag(takes_context=True)
def pagination_url(context, page):
    request = context['request']
    dict_ = request.GET.copy()

    page_kwarg = context.get('page_kwarg')
    if page_kwarg:
        dict_[page_kwarg] = page

    return dict_.urlencode()
