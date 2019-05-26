from django.contrib import admin
from adminsortable2.admin import SortableInlineAdminMixin

from .models import Unit, UnitConversion, Tag, Ingredient, Recipe
from .models import IngredientInRecipe
from .forms import RecipeForm, IngredientInRecipeForm


class IngredientInRecipeInline(SortableInlineAdminMixin, admin.TabularInline):

    model = IngredientInRecipe
    form = IngredientInRecipeForm
    extra = 10

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else self.extra


class RecipeAdmin(admin.ModelAdmin):

    form = RecipeForm
    inlines = (IngredientInRecipeInline,)

    class Media:
        css = {
            'all': ('hide_admin_original.css',),
        }


admin.site.register(Unit, admin.ModelAdmin)
admin.site.register(UnitConversion, admin.ModelAdmin)
admin.site.register(Tag, admin.ModelAdmin)
admin.site.register(Ingredient, admin.ModelAdmin)
admin.site.register(Recipe, RecipeAdmin)
