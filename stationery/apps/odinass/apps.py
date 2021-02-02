from django.apps import AppConfig


class OdinAssConfig(AppConfig):
    name = 'odinass'
    verbose_name = '1C'

    def ready(self):
        import odinass.signals