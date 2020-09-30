import io
import re
import csv
import datetime
import requests
import itertools
import traceback

from decimal import Decimal

from django.conf import settings
from django.forms import modelform_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import F, Q
from django.shortcuts import render, redirect
from django.utils.formats import localize
from django.utils.translation import gettext as _
from dal import autocomplete
from constance import config

from .models import (
    Alias,
    Dishes,
    IngredientInRecipe,
    IngredientUnit,
    Menu,
    Recipe,
    Tag,
)
from .models import normalize


OURGROCERIES_SIGNIN_URL = 'https://www.ourgroceries.com/sign-in'
OURGROCERIES_LIST_URL = 'https://www.ourgroceries.com/your-lists/'

DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']


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
        'ingredient_units': recipe.ingredientinrecipe_set.all(),
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

    base_qs = (IngredientInRecipe.objects
               .filter(recipe__pk__in=recipe_pks)
               .exclude(ingredient_unit__ingredient__name='')
               .exclude(ingredient_unit__unit__isnull=True)
               .exclude(ingredient_unit__ingredient__category__isnull=True))
    primary_filter = (
        Q(ingredient_unit__ingredient__primary_unit__isnull=True) |
        Q(ingredient_unit__factor__isnull=True) |
        Q(ingredient_unit__unit=F('ingredient_unit__ingredient__primary_unit'))
    )
    primary_qs = base_qs.filter(primary_filter)
    not_primary_qs = base_qs.exclude(primary_filter)

    totals = {
        pk: 0
        for pk in primary_qs.values_list('ingredient_unit__pk', flat=True)
    }
    new_primary = set()
    for recipe, qty in recipes:
        for ingredient_in_recipe in recipe.ingredientinrecipe_set.all():
            if not_primary_qs.filter(pk=ingredient_in_recipe.pk).exists():
                ingredient = ingredient_in_recipe.ingredient_unit.ingredient
                pk = (IngredientUnit.objects
                      .get(ingredient=ingredient, unit=ingredient.primary_unit)
                      .pk)
                factor = ingredient_in_recipe.ingredient_unit.factor
                if pk not in totals:
                    totals[pk] = 0
                    new_primary.add(pk)
            else:
                pk = ingredient_in_recipe.ingredient_unit.pk
                factor = 1
            if pk in totals:
                totals[pk] += ingredient_in_recipe.amount * qty * factor

    ingredient_units = []
    for ingredient_unit in (
        IngredientUnit.objects
            .filter(pk__in=totals)
            .select_related('ingredient', 'unit')
            .order_by('ingredient__category')
            .distinct()
    ):
        ingredient_units.append([{
            'pk': ingredient_unit.pk,
            'name': ingredient_unit.ingredient.display_name,
            'category': ingredient_unit.ingredient.category.name,
            'unit': ingredient_unit.unit.name,
            'unit_pk': ingredient_unit.unit.pk,
        }, 0])

    for i, (ingredient_unit, total) in enumerate(ingredient_units):
        ingredient_units[i][1] = normalize(totals[ingredient_unit['pk']])
    if not ingredient_units:
        message = _('No recipes were added to the cart yet')

    if action == 'OurGroceries':
        dishes = Dishes.objects.get()
        for recipe, qty in recipes:
            if dishes.dishes and not dishes.dishes.endswith('\r\n'):
                dishes.dishes += '\r\n'
            dishes.dishes += '{} ({})\r\n'.format(recipe, qty)
        dishes.save()

        if not request.user.is_authenticated:
            return redirect(
                '{}?next={}'.format(reverse(settings.LOGIN_URL), request.path)
            )
        if not (config.OURGROCERIES_USERNAME and
                config.OURGROCERIES_PASSWORD and
                config.OURGROCERIES_LIST):
            error = _('OurGroceries is not completely configured')

        selected = [int(pk) for pk in request.POST.getlist('ingredient_unit')]
        try:
            add_to_ourgroceries(ingredient_units, selected)
            message = _('Items succesfully added to OurGroceries')
            recipes, ingredient_units = [], []
        except Exception:
            error = _('Encountered an error adding items to OurGroceries')
            tb = traceback.format_exc()
        else:
            request.session['cart'] = {}
            request.session.save()

    return render(request, 'cart.html', context={
        'page': 'cart',
        'recipes': recipes,
        'ingredient_units': ingredient_units,
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


def del_from_cart(request, pk):
    del request.session['cart'][pk]
    request.session.save()
    return HttpResponseRedirect(reverse('cart'))


def add_to_ourgroceries(ingredient_units, selected):
    if not selected or settings.DEBUG:
        return

    # Build csv
    rows = [
        (
            '{}{}'.format(
                ingredient_unit['name'],
                ' ({})'.format(
                    localize(total)
                    if ingredient_unit['unit_pk'] == 1
                    else '{}{}'.format(
                        localize(total),
                        ingredient_unit['unit']))
                if (total and
                    (not ingredient_unit['unit_pk'] == 1 or
                     total > 1))
                else ''
            ),
            ingredient_unit['category']
        )
        for ingredient_unit, total in ingredient_units
        if ingredient_unit['pk'] in selected
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


def menu(request):
    MenuForm = modelform_factory(Menu, fields='__all__')
    dishes, _ = Dishes.objects.get_or_create()
    menu, _ = Menu.objects.get_or_create()

    if request.method == 'POST':
        dishes.dishes = request.POST['dishes']
        dishes.save()

        menu = Menu.objects.get(pk=request.POST['pk'])
        form = MenuForm(request.POST, instance=menu)
        if form.is_valid():
            form.save()
    else:
        form = MenuForm(instance=menu)

    return render(request, 'menu.html', {
        'page': 'menu',
        'days': DAYS_OF_THE_WEEK,
        'day_of_week': DAYS_OF_THE_WEEK[datetime.date.today().weekday()],
        'meals': ['lunch', 'dinner'],
        'dishes': dishes.dishes,
        'menu': menu,
        'form': form,
    })


class TagAutoComplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.q:
            return Tag.objects.filter(name__istartswith=self.q)
        else:
            return Tag.objects.all()


class IngredientAutoComplete(autocomplete.Select2QuerySetView):

    class IngredientUnitOrAlias:

        def __init__(self, ingredient_unit, alias=None):
            if alias:
                self.name = alias.name
            else:
                self.name = ingredient_unit.ingredient.name
            self.pk = ingredient_unit.pk
            self.unit = ingredient_unit.unit

        def __str__(self):
            return '{} ({})'.format(self.name, self.unit)

    def get_queryset(self):
        if self.q:
            ingredient_units = IngredientUnit.objects.filter(
                ingredient__name__icontains=self.q)
            aliases = Alias.objects.filter(name__icontains=self.q)
        else:
            ingredient_units = IngredientUnit.objects.all()
            aliases = Alias.objects.all()
        l1 = [self.IngredientUnitOrAlias(ingredient_unit)
              for ingredient_unit in ingredient_units]
        l2 = list(itertools.chain(*[
            [self.IngredientUnitOrAlias(ingredient_unit, alias)
             for ingredient_unit in alias.ingredient.ingredientunit_set.all()]
            for alias in aliases]))
        return sorted(l1 + l2, key=lambda x: str(x).lower())
