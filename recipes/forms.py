from dal import autocomplete

from django import forms
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from martor.fields import MartorFormField

from .models import (
    Ingredient, IngredientUnit, Unit, UnitConversion, IngredientInRecipe,
    Recipe, get_factor)


class IngredientForm(forms.ModelForm):

    class Meta:
        model = Ingredient
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['shopping_unit'].widget.can_add_related = False
            self.fields['shopping_unit'].widget.can_change_related = False
            self.fields['shopping_unit'].widget.can_delete_related = False


class IngredientUnitInlineForm(forms.ModelForm):

    class Meta:
        model = IngredientUnit
        fields = '__all__'
        localized_fields = ['factor']


class UnitConversionForm(forms.ModelForm):

    class Meta:
        model = UnitConversion
        fields = '__all__'
        localized_fields = ['factor']


class IngredientInRecipeForm(forms.ModelForm):
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        empty_label='',
        required=False,
        label=_('unit'))

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'
        localized_fields = ['amount']
        widgets = {
            'ingredient_unit': autocomplete.ModelSelect2(
                url='autocomplete-ingredient'),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['unit'] = instance.ingredient_unit.unit
        super().__init__(*args, **kwargs)

    def clean(self):
        ingredient_unit = self.cleaned_data['ingredient_unit']
        unit = self.cleaned_data.get('unit')
        if unit is None:
            unit = ingredient_unit.unit

        factor = get_factor(ingredient_unit, unit)
        if factor is None:
            raise forms.ValidationError(
                format_lazy(_('No unit conversion from {} to {}'),
                            unit, ingredient_unit.unit))
        elif not factor == 1:
            amount = self.cleaned_data['amount'] / factor
            self.cleaned_data['amount'] = round(amount, 3)
        return super().clean()


class RecipeForm(forms.ModelForm):
    recipe = MartorFormField()

    class Meta:
        model = Recipe
        fields = '__all__'
        widgets = {
            'tags': autocomplete.ModelSelect2Multiple(url='autocomplete-tag'),
        }
