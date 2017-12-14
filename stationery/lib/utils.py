def l(url, name, **kwargs):
    """
    Формирует html тег <a>
    """
    kwargs.update(href=url)
    attrs = ' '.join(['%s="%s"' % (attr,
                                   value) for attr, value in kwargs.items()])
    return '<a %s>%s</a>' % (attrs, name)
