from constance import config as constance_config

from filebrowser.base import FileObject

from odinass.models import Category

from .models import Vkvidjet,FooterImg,Color,SocialLink,HeaderLogo,ImgCategory,ColorTopHead, MenuPage, Page


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
    categories = Category.objects.root_nodes().filter(is_published=True)
    full_categories = Category.objects.all()
    solo_menu = Page.objects.filter(in_menu=True)

    page_menu = MenuPage.objects.all()

    print(solo_menu)

    return {
        'categories': categories,
        'full_categories': full_categories,
        'page_menu': page_menu,
        'solo_menu': solo_menu,
    }

def Vkwidget(request):
    vkwidgets = Vkvidjet.objects.all()
    return {
        'vkwidgets':vkwidgets
    }

def get_footer_color(request):
    social = SocialLink.objects.all().order_by('sort')
    footer = FooterImg.objects.all().first()
    header = Color.objects.all().order_by('title')
    logo = HeaderLogo.objects.all()
    imgcategory = ImgCategory.objects.all().order_by('title')
    colortop = ColorTopHead.objects.first()
    return {'footer_color':footer,'header_color':header,'social_links':social,'logo':logo,'imgcategory':imgcategory, 'color_top':colortop}
