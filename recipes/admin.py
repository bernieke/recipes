from django.contrib import admin
from django.urls import reverse_lazy
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django_markdown.admin import AdminMarkdownWidget

from .models import (
    Unit, UnitConversion,
    Category, Tag,
    Ingredient, Alias,
    Recipe, IngredientInRecipe)
from .forms import UnitConversionForm, RecipeForm, IngredientInRecipeForm


admin.site.site_url = reverse_lazy('index')


class UnitAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class UnitConversionAdmin(admin.ModelAdmin):
    form = UnitConversionForm


class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class TagAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'break_after')


class AliasInline(admin.TabularInline):
    model = Alias
    extra = 0


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
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
    formfield_overrides = {'recipe': {'widget': AdminMarkdownWidget}}

    class Media:
        css = {
            'all': ('hide_admin_original.css',),
        }


admin.site.register(Unit, UnitAdmin)
admin.site.register(UnitConversion, UnitConversionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
