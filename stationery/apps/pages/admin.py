from django import forms
from django.contrib import admin

from adminsortable2.admin import SortableAdminMixin

from pages.models import Page, Blog, Slider, MenuPage

from .models import Vkvidjet,FooterImg,Color,SocialLink,HeaderLogo,ImgCategory,ColorTopHead,ImagePage



class PageAdmin(admin.TabularInline):

    model = Page

    prepopulated_fields = {
        'slug': (
            'title',
        )
    }

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'slug',
                'icon',
                'content',
            ),
        }),
    )

class ImagePageAdmin(admin.TabularInline):
    def get_href(self,obj):
        return 'https://kancmiropt.ru' + obj.url_img.url
    readonly_fields = ('get_href',)
    model = ImagePage

    get_href.short_description = 'Ссылка на изображение'


@admin.register(MenuPage)
class MenuPageAdmin(admin.ModelAdmin):
    list_display = ('title', )
    inlines = [PageAdmin, ] 


@admin.register(Page)  
class TransferPageAdmin(admin.ModelAdmin):

    prepopulated_fields = {
        'slug': (
            'title',
        )
    }

    fieldsets = (
        (None, {
            'fields': (
                'title',
                'slug',
                'icon',
                'content',
                'page',
                'in_menu',
            ),
        }),
    )

    inlines = [ImagePageAdmin, ] 

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    pass


class SliderFormAdmin(forms.ModelForm):
    class Meta:
        fields = '__all__'

        widgets = {
            'background': forms.TextInput(attrs={'type': 'color'}),
        }


@admin.register(Slider)
class SliderAdmin(SortableAdminMixin, admin.ModelAdmin):
    form = SliderFormAdmin


admin.site.register(Vkvidjet)

class ColorFormAdmin(forms.ModelForm):
    class Meta:
        fields = '__all__'

        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

@admin.register(FooterImg)
class FooterAdmin(admin.ModelAdmin):
    form = ColorFormAdmin

@admin.register(Color)
class FooterAdmin(admin.ModelAdmin):
    form = ColorFormAdmin

@admin.register(ColorTopHead)
class ColorTopHeadAdmin(admin.ModelAdmin):
    form = ColorFormAdmin

admin.site.register(SocialLink)
admin.site.register(HeaderLogo)
admin.site.register(ImgCategory)
