from django.apps import AppConfig
from django.db.models.signals import post_migrate, post_save


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Сайт"

    def ready(self):
        from . import i18n
        from .models import UiText

        post_migrate.connect(lambda **kw: i18n.sync_keys(), sender=self, weak=False)
        post_save.connect(lambda **kw: i18n.invalidate(), sender=UiText, weak=False)
