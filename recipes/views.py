from django.shortcuts import render
from dal import autocomplete

from .models import Tag, Ingredient, Recipe


def index(request):
    return render(request, 'index.html', context={
        'tag_recipes': [
            (tag, tag.recipe_set.all()) for tag in Tag.objects.all()
        ]
    })


def recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    return render(request, 'recipe.html', context={
        'recipe': recipe,
        'ingredients': ['{}{} {}'.format(
            ingredient_in_recipe.amount,
            ingredient_in_recipe.ingredient.unit.name,
            ingredient_in_recipe.ingredient.name,
        ) for ingredient_in_recipe in recipe.ingredientinrecipe_set.all()],
        'tags': recipe.tags.all().values_list('name', flat=True),
    })


class TagAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Tag.objects.filter(name__istartswith=self.q)
        else:
            return Tag.objects.all()


class IngredientAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Ingredient.objects.filter(name__istartswith=self.q)
        else:
            return Ingredient.objects.all()
