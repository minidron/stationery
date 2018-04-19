from dynamic_preferences import types
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry


general = Section('фон')


@global_preferences_registry.register
class SiteBackgroundColor(types.StringPreference):
    default = '#F7F7F7'
    name = 'цвет'
    section = general


@global_preferences_registry.register
class SiteBackground(types.FilePreference):
    name = 'изображение'
    section = general


@global_preferences_registry.register
class SiteBackgroundPreference(types.ChoicePreference):
    default = '1'
    name = 'заполнение'
    section = general

    choices = [
        ('1', 'Не повторять'),
        ('2', 'Повторять'),
    ]
