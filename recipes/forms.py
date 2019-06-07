from dal import autocomplete

from django import forms
from django.utils.text import format_lazy
from django.utils.translation import gettext_lazy as _
from django_markdown.fields import MarkdownFormField

from .models import Unit, UnitConversion, IngredientInRecipe, Recipe


class UnitConversionForm(forms.ModelForm):

    class Meta:
        model = UnitConversion
        fields = '__all__'
        localized_fields = ('factor',)


class IngredientInRecipeForm(forms.ModelForm):
    unit = forms.ModelChoiceField(
        queryset=Unit.objects.all(),
        empty_label=None,
        label=_('unit'),
        initial=1)

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'
        localized_fields = ('amount',)
        widgets = {
            'ingredient': autocomplete.ModelSelect2(
                url='autocomplete-ingredient'),
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        if instance:
            if 'initial' not in kwargs:
                kwargs['initial'] = {}
            kwargs['initial']['unit'] = instance.ingredient.unit
        super().__init__(*args, **kwargs)

    def clean(self):
        unit = self.cleaned_data['unit']
        ingredient = self.cleaned_data['ingredient']
        if not unit == ingredient.unit:
            try:
                uc = UnitConversion.objects.get(
                    from_unit=unit, to_unit=ingredient.unit)
            except UnitConversion.DoesNotExist:
                raise forms.ValidationError(
                    format_lazy(_('No unit conversion from {} to {}'),
                                unit, ingredient.unit))
            self.cleaned_data['amount'] *= uc.factor
        return super().clean()


class RecipeForm(forms.ModelForm):
    recipe = MarkdownFormField()

    class Meta:
        model = Recipe
        fields = '__all__'
        widgets = {
            'tags': autocomplete.ModelSelect2Multiple(url='autocomplete-tag'),
        }
