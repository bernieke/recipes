from django.contrib import admin
from django.urls import reverse_lazy
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from martor.widgets import AdminMartorWidget

from .models import (
    Unit, UnitConversion, IngredientUnit, Category, Tag, Ingredient, Alias,
    Recipe, IngredientInRecipe, Menu, MenuTemplate)
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
    list_display = ['name', 'break_after']
    fields = ['name', 'break_after', 'recipes']
    readonly_fields = ['recipes']


class IngredientUnitInline(admin.TabularInline):
    model = IngredientUnit
    form = IngredientUnitInlineForm
    extra = 0


class AliasInline(SortableInlineAdminMixin, admin.TabularInline):
    model = Alias
    extra = 0


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'units', 'aliases']
    form = IngredientForm
    inlines = [IngredientUnitInline, AliasInline]
    fields = ['name', 'primary_unit', 'category', 'recipes']
    readonly_fields = ['recipes']
    search_fields = ['name', 'alias__name']

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
    list_display = ['title', 'tag_list']
    inlines = [IngredientInRecipeInline]
    formfield_overrides = {'recipe': {'widget': AdminMartorWidget}}
    search_fields = ['title', 'tags__name']

    class Media:
        css = {
            'all': ['hide_admin_original.css'],
        }

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['title'].widget.attrs['style'] = 'width: 40em;'
        form.base_fields['tags'].widget.attrs['style'] = 'width: 41em;'
        return form


class BaseMenuAdmin(admin.ModelAdmin):

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        for key in form.base_fields:
            if (key == 'name' or
                    key.endswith('_note') or
                    key.endswith('_dishes')):
                form.base_fields[key].widget.attrs['style'] = 'width: 20em;'
                form.base_fields[key].widget.attrs['rows'] = '1'
        return form


class MenuAdmin(BaseMenuAdmin):
    fieldsets = [
        ('Notes', {
            'fields': [
                ('monday_lunch_note', 'monday_dinner_note'),
                ('monday_lunch_dishes', 'monday_dinner_dishes'),
                ('tuesday_lunch_note', 'tuesday_dinner_note'),
                ('tuesday_lunch_dishes', 'tuesday_dinner_dishes'),
                ('wednesday_lunch_note', 'wednesday_dinner_note'),
                ('wednesday_lunch_dishes', 'wednesday_dinner_dishes'),
                ('thursday_lunch_note', 'thursday_dinner_note'),
                ('thursday_lunch_dishes', 'thursday_dinner_dishes'),
                ('friday_lunch_note', 'friday_dinner_note'),
                ('friday_lunch_dishes', 'friday_dinner_dishes'),
                ('saturday_lunch_note', 'saturday_dinner_note'),
                ('saturday_lunch_dishes', 'saturday_dinner_dishes'),
                ('sunday_lunch_note', 'sunday_dinner_note'),
                ('sunday_lunch_dishes', 'sunday_dinner_dishes'),
            ],
        }),
    ]
    list_display = ['year', 'week']


class MenuTemplateAdmin(BaseMenuAdmin):
    fieldsets = [
        (None, {
            'fields': ['name', 'active'],
        }),
        ('Notes', {
            'fields': [
                ('monday_lunch_note', 'monday_dinner_note'),
                ('tuesday_lunch_note', 'tuesday_dinner_note'),
                ('wednesday_lunch_note', 'wednesday_dinner_note'),
                ('thursday_lunch_note', 'thursday_dinner_note'),
                ('friday_lunch_note', 'friday_dinner_note'),
                ('saturday_lunch_note', 'saturday_dinner_note'),
                ('sunday_lunch_note', 'sunday_dinner_note'),
            ],
        }),
    ]
    list_display = ['name', 'active']


admin.site.register(Unit, UnitAdmin)
admin.site.register(UnitConversion, UnitConversionAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuTemplate, MenuTemplateAdmin)
