import io
import re
import csv
import requests
import traceback

from decimal import Decimal

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.formats import localize
from django.utils.translation import gettext as _
from dal import autocomplete
from constance import config

from .models import Tag, Alias, Ingredient, IngredientInRecipe, Recipe
from .models import normalize


OURGROCERIES_SIGNIN_URL = 'https://www.ourgroceries.com/sign-in'
OURGROCERIES_LIST_URL = 'https://www.ourgroceries.com/your-lists/'


def index(request):
    return render(request, 'index.html', context={
        'page': 'index',
        'tags': Tag.objects.all(),
        'selected_tag': None,
        'recipes': Recipe.objects.all(),
    })


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
        'ingredients': recipe.ingredientinrecipe_set.all(),
        'tags': recipe.tags.all().values_list('name', flat=True),
    })


def cart(request):
    message, error, tb = None, None, None
    action = request.POST.get('action')

    if action == 'edit':
        pk = request.POST.get('pk')
        qty = request.POST.get('qty')
        if request.session.get('cart') and pk in request.session['cart']:
            if Decimal(qty) > 0:
                request.session['cart'][pk] = qty
            else:
                del request.session['cart'][pk]
            request.session.save()

    recipe_pks = request.session.get('cart', {})
    recipes = [
        (recipe, Decimal(request.session['cart'][str(recipe.pk)]))
        for recipe in Recipe.objects.filter(pk__in=recipe_pks)]
    ingredients = [
        [ingredient, 0] for ingredient in (
            IngredientInRecipe.objects
            .filter(recipe__pk__in=recipe_pks)
            .select_related('ingredient', 'ingredient__unit')
            .exclude(ingredient__name='')
            .exclude(ingredient__unit__isnull=True)
            .exclude(ingredient__category__isnull=True)
            .values('ingredient__pk',
                    'ingredient__name',
                    'ingredient__category__name',
                    'ingredient__unit__pk',
                    'ingredient__unit__name')
            .order_by('ingredient__category')
            .distinct()
        )
    ]

    totals = {ingredient['ingredient__pk']: total
              for ingredient, total in ingredients}
    for recipe, qty in recipes:
        for ingredient_in_recipe in recipe.ingredientinrecipe_set.all():
            pk = ingredient_in_recipe.ingredient.pk
            if pk in totals:
                totals[pk] += ingredient_in_recipe.amount * qty
    for i, (ingredient, total) in enumerate(ingredients):
        ingredients[i][1] = normalize(totals[ingredient['ingredient__pk']])
    if not ingredients:
        message = _('No recipes were added to the cart yet')

    if action == 'OurGroceries':
        if not request.user.is_authenticated:
            return redirect(
                '{}?next={}'.format(reverse(settings.LOGIN_URL), request.path)
            )
        if not (config.OURGROCERIES_USERNAME and
                config.OURGROCERIES_PASSWORD and
                config.OURGROCERIES_LIST):
            error = _('OurGroceries is not completely configured yet')

        selected = [int(pk) for pk in request.POST.getlist('ingredient')]
        if selected:
            try:
                add_to_ourgroceries(ingredients, selected)
                message = _('Items succesfully added to OurGroceries')
                recipes, ingredients = [], []
            except Exception:
                error = _('Encountered an error adding items to OurGroceries')
                tb = traceback.format_exc()
            else:
                request.session['cart'] = {}
                request.session.save()
        else:
            error = _('Nothing has been selected')

    return render(request, 'cart.html', context={
        'page': 'cart',
        'recipes': recipes,
        'ingredients': ingredients,
        'message': message,
        'error': error,
        'traceback': tb,
    })


def add_to_cart(request, pk):
    if not request.session.get('cart'):
        request.session['cart'] = {}
    if pk not in request.session['cart']:
        request.session['cart'][pk] = 0
    request.session['cart'][pk] += 1
    request.session.save()
    return HttpResponse('')


def add_to_ourgroceries(ingredients, selected):
    # Build csv
    rows = [
        (
            '{}{}'.format(
                ingredient['ingredient__name'],
                ' ({})'.format(
                    localize(total)
                    if ingredient['ingredient__unit__pk'] == 1
                    else '{}{}'.format(
                        localize(total), ingredient['ingredient__unit__name']))
                if not ingredient['ingredient__unit__pk'] == 1 or total > 1
                else ''
            ),
            ingredient['ingredient__category__name']
        )
        for ingredient, total in ingredients
        if ingredient['ingredient__pk'] in selected
    ]
    f = io.StringIO()
    csv.writer(f).writerows([('description', 'category')] + rows)
    f.seek(0)

    # Login
    s = requests.Session()
    s.post('https://www.ourgroceries.com/sign-in', data={
        'emailAddress': config.OURGROCERIES_USERNAME,
        'action': 'sign-me-in',
        'password': config.OURGROCERIES_PASSWORD,
        'staySignedIn': 'off',
    }, headers={
        'Referer': OURGROCERIES_SIGNIN_URL,
        'Origin': 'https://www.ourgroceries.com',
    }).raise_for_status()

    r = s.get(OURGROCERIES_LIST_URL)
    r.raise_for_status()

    # Get list id
    team_id = re.search('g_teamId = "(.*)"', r.text).groups(0)[0]
    r = s.post(OURGROCERIES_LIST_URL, json={
        'command': 'getOverview',
        'teamId': team_id,
    }, headers={
        'Referer': OURGROCERIES_LIST_URL,
        'Origin': 'https://www.ourgroceries.com',
        'Accept': 'application/json, text/javascript, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.ourgroceries.com',
        'Content-Type': 'application/json',
    })
    r.raise_for_status()

    # Post csv
    for shopping_list in r.json()['shoppingLists']:
        if shopping_list['name'] == config.OURGROCERIES_LIST:
            list_id = shopping_list['id']
            break
    else:
        raise RuntimeError(
            'No shopping list named {} on OurGroceries for {}'.format(
                config.OURGROCERIES_LIST, config.OURGROCERIES_USERNAME))
    s.post(OURGROCERIES_LIST_URL, files={
        'command': 'importItems',
        'listId': list_id,
        'items': '',
        'importFile': ('shopping.csv', f)
    }, headers={
        'Referer': '{}list/{}'.format(OURGROCERIES_LIST_URL, list_id),
        'Origin': 'https://www.ourgroceries.com',
        'Host': 'www.ourgroceries.com',
    }).raise_for_status()


class TagAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Tag.objects.filter(name__istartswith=self.q)
        else:
            return Tag.objects.all()


class IngredientAutoComplete(autocomplete.Select2QuerySetView):

    class IngredientOrAlias:

        def __init__(self, ingredient_or_alias):
            if isinstance(ingredient_or_alias, Ingredient):
                ingredient = ingredient_or_alias
            elif isinstance(ingredient_or_alias, Alias):
                ingredient = ingredient_or_alias.ingredient

            self.name = ingredient_or_alias.name
            self.pk = ingredient.pk
            self.unit = ingredient.unit

        def __str__(self):
            return '{} ({})'.format(self.name, self.unit)

    def get_queryset(self):
        if self.q:
            ingredients = Ingredient.objects.filter(name__icontains=self.q)
            aliases = Alias.objects.filter(name__icontains=self.q)
        else:
            ingredients = Ingredient.objects.all()
            aliases = Alias.objects.all()
        l1 = [self.IngredientOrAlias(ingredient) for ingredient in ingredients]
        l2 = [self.IngredientOrAlias(alias) for alias in aliases]
        return sorted(l1 + l2, key=lambda x: str(x))
