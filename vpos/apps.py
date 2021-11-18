
from django.apps import AppConfig


class VposConfig(AppConfig):

    name = 'vpos'
    verbose_name = 'Django vPOS'

    def ready(self) -> None:
        from vpos.configs import conf
        conf.validate()
