from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin

from .models import (
    Unit, UnitConversion,
    Category, Tag,
    Ingredient, Alias,
    Recipe, IngredientInRecipe)
from .forms import UnitConversionForm, RecipeForm, IngredientInRecipeForm


class UnitConversionAdmin(admin.ModelAdmin):
    form = UnitConversionForm


class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class TagAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class AliasInline(admin.TabularInline):
    model = Alias
    extra = 0


class IngredientAdmin(admin.ModelAdmin):
    inlines = (AliasInline,)


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
admin.site.register(UnitConversion, UnitConversionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
