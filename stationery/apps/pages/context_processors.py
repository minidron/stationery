from constance import config as constance_config

from filebrowser.base import FileObject

from odinass.models import Category

from orders.models import Order


def config(request):
    background_image = ''
    if constance_config.BACKGROUND_IMAGE:
        background_image = FileObject(constance_config.BACKGROUND_IMAGE).url

    return {
        'background_repeat': constance_config.BACKGROUND_REPEAT,
        'background_image': background_image,
        'background_color': constance_config.BACKGROUND_COLOR,
        'background_attachment': constance_config.BACKGROUND_ATTACHMENT,
    }


def menu(request):
    user = request.user
    categories = Category.objects.root_nodes().filter(is_published=True)

    return {
        'categories': categories,
        'cart': Order.get_cart(user) if not user.is_anonymous else None,
    }
