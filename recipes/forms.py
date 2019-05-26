from dal import autocomplete

from django import forms

from .models import Recipe, IngredientInRecipe


class RecipeForm(forms.ModelForm):

    class Meta:
        model = Recipe
        fields = '__all__'
        widgets = {
            'tags': autocomplete.ModelSelect2Multiple(url='autocomplete-tag'),
        }


class IngredientInRecipeForm(forms.ModelForm):

    class Meta:
        model = IngredientInRecipe
        fields = '__all__'
        widgets = {
            'ingredient': autocomplete.ModelSelect2(
                url='autocomplete-ingredient'),
        }
