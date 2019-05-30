import vinaigrette

from django.apps import AppConfig


class RecipesConfig(AppConfig):
    name = 'recipes'

    def ready(self):
        from .models import Unit

        vinaigrette.register(Unit, ['name'])
