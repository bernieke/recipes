from decimal import Context

from django.conf import settings
from django.http import HttpResponse
from django.db.models import Sum
from django.shortcuts import render, redirect
from dal import autocomplete

from .models import Tag, Ingredient, IngredientInRecipe, Recipe


def normalize(d):
    normalized = d.normalize(Context(settings.AMOUNT_PRECISION))
    threshold = 10 ** settings.AMOUNT_PRECISION
    return int(normalized) if d >= threshold else normalized


def index(request):
    return redirect(Tag.objects.first())


def cart(request):
    recipes = Recipe.objects.filter(pk__in=request.session.get('cart', []))
    ingredients = (IngredientInRecipe.objects
                   .filter(recipe__in=recipes,
                           ingredient__category__isnull=False)
                   .select_related('ingredient', 'ingredient__unit')
                   .values('ingredient__pk', 'ingredient__name',
                           'ingredient__unit__name')
                   .annotate(total=Sum('amount'))
                   .order_by('ingredient__category'))
    print(ingredients)
    return render(request, 'cart.html', context={
        'page': 'cart',
        'recipes': recipes,
        'ingredients': ingredients,
    })


def add_to_cart(request, pk):
    if not request.session.get('cart'):
        request.session['cart'] = []
    request.session['cart'].append(pk)
    request.session.save()
    return HttpResponse('')


def tag(request, pk):
    tag = Tag.objects.get(pk=pk)
    return render(request, 'index.html', context={
        'page': 'index',
        'tags': Tag.objects.all(),
        'selected_tag': tag,
        'recipes': tag.recipe_set.all(),
    })


def recipe(request, pk):
    recipe = Recipe.objects.get(pk=pk)
    return render(request, 'recipe.html', context={
        'page': 'recipe',
        'recipe': recipe,
        'ingredients': ['{}{} {}'.format(
            normalize(ingredient_in_recipe.amount),
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
