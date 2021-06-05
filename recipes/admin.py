from django.contrib import admin
from django.urls import reverse_lazy
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from django_markdown.admin import AdminMarkdownWidget

from .models import (
    Unit, UnitConversion, IngredientUnit, Category, Tag, Ingredient, Alias,
    Recipe, IngredientInRecipe)
from .forms import (
    IngredientForm, IngredientUnitInlineForm, UnitConversionForm,
    RecipeForm, IngredientInRecipeForm)


admin.site.site_url = reverse_lazy('index')


class UnitAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class UnitConversionAdmin(admin.ModelAdmin):
    form = UnitConversionForm


class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    pass


class TagAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'break_after')
    fields = ('name', 'break_after', 'recipes')
    readonly_fields = ('recipes',)


class IngredientUnitInline(admin.TabularInline):
    model = IngredientUnit
    form = IngredientUnitInlineForm
    extra = 0


class AliasInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Alias
    extra = 0


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'units', 'aliases')
    form = IngredientForm
    inlines = (IngredientUnitInline, AliasInline)
    fields = ('name', 'primary_unit', 'category', 'recipes')
    readonly_fields = ('recipes',)
    search_fields = ('name', 'alias__name')

    def aliases(self, obj):
        return ', '.join(alias.name for alias in obj.alias_set.all())


class IngredientInRecipeInline(SortableInlineAdminMixin, admin.TabularInline):
    model = IngredientInRecipe
    form = IngredientInRecipeForm
    extra = 10

    def get_extra(self, request, obj=None, **kwargs):
        return 0 if obj else self.extra


class RecipeAdmin(admin.ModelAdmin):
    form = RecipeForm
    list_display = ('title', 'tag_list')
    inlines = (IngredientInRecipeInline,)
    formfield_overrides = {'recipe': {'widget': AdminMarkdownWidget}}
    search_fields = ('title', 'tags__name')

    class Media:
        js = [
            'admin/js/jquery.init.js',
            'django_markdown/jquery.init.js',
        ]
        css = {
            'all': ('hide_admin_original.css',),
        }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['title'].widget.attrs['style'] = 'width: 40em;'
        form.base_fields['tags'].widget.attrs['style'] = 'width: 41em;'
        return form


admin.site.register(Unit, UnitAdmin)
admin.site.register(UnitConversion, UnitConversionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
