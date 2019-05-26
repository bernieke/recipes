from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin

from .models import Unit, UnitConversion, Tag, Ingredient, Recipe
from .models import IngredientInRecipe


class IngredientInRecipeInline(SortableInlineAdminMixin, admin.TabularInline):

    model = IngredientInRecipe
    extra = 10


class RecipeAdmin(admin.ModelAdmin):

    inlines = (IngredientInRecipeInline,)


admin.site.register(Unit, admin.ModelAdmin)
admin.site.register(UnitConversion, admin.ModelAdmin)
admin.site.register(Tag, admin.ModelAdmin)
admin.site.register(Ingredient, admin.ModelAdmin)
admin.site.register(Recipe, RecipeAdmin)
