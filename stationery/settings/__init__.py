import os

from stationery.settings.common import *  # NOQA

DJANGO_CONF = os.environ.get('DJANGO_CONF', 'default')
if DJANGO_CONF != 'default':
    module = __import__('%s.%s' % (__name__, DJANGO_CONF),
                        globals(), locals(), ['*'])
    for k in dir(module):
        locals()[k] = getattr(module, k)

try:
    from stationery.settings.local import *  # NOQA
except ImportError:
    pass
