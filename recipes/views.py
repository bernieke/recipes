import csv
import functools
import io
import itertools
import json
import re
import requests
import traceback

from datetime import date, datetime, timedelta
from decimal import Decimal

from constance import config
from dal import autocomplete
from django.conf import settings
from django.contrib.auth import views
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.formats import localize
from django.utils.translation import gettext as _

from .models import (
    get_factor,
    normalize,
    Alias,
    Dishes,
    IngredientInRecipe,
    IngredientUnit,
    Menu,
    Recipe,
    Tag,
    MenuTemplate,
)


OURGROCERIES_SIGNIN_URL = 'https://www.ourgroceries.com/sign-in'
OURGROCERIES_LIST_URL = 'https://www.ourgroceries.com/your-lists/'

DAYS_OF_THE_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday']


class persist_session_vars(object):

    def __init__(self, vars):
        self.vars = vars

    def __call__(self, view_func):

        @functools.wraps(view_func)
        def inner(request, *args, **kwargs):
            # Backup first
            session_backup = {}
            for var in self.vars:
                try:
                    session_backup[var] = request.session[var]
                except KeyError:
                    pass

            # Call the original view
            response = view_func(request, *args, **kwargs)

            # Restore variables in the new session
            for var, value in session_backup.items():
                request.session[var] = value

            return response

        return inner


@persist_session_vars(['cart', 'ingredient_sel', 'order'])
def login(request, *args, **kwargs):
    return views.login(request, *args, **kwargs)


def save_order(func):
    def wrapper(request, *args, **kwargs):
        order = request.GET.get('order')
        if order is None and 'order' not in request.session:
            order = '-popularity'
        if order is not None:
            request.session['order'] = order
        return func(request, *args, **kwargs)
    return wrapper


@save_order
def index(request):
    order = request.session['order']
    if order == 'title':
        order_list = []
    else:
        order_list = [order]
    order_list.append(Lower('title'))
    return render(request, 'index.html', context={
        'page': 'index',
        'tags': Tag.objects.all(),
        'selected_tag': None,
        'recipes': Recipe.objects.all().order_by(*order_list),
        'order': order,
    })


@save_order
def tag(request, pk):
    order = request.session['order']
    tag = Tag.objects.get(pk=pk)
    return render(request, 'index.html', context={
        'page': 'index',
        'tags': Tag.objects.all(),
        'selected_tag': tag,
        'recipes': tag.recipe_set.all().order_by(order),
        'order': order,
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
    ingredient_sel = [int(x) for x in request.POST.getlist('ingredient_unit')]
    if ingredient_sel:
        request.session['ingredient_sel'] = ingredient_sel
        request.session.save()
    else:
        ingredient_sel = request.session.get('ingredient_sel', [])
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
            ingredient_unit = ingredient_in_recipe.ingredient_unit
            if not_primary_qs.filter(pk=ingredient_in_recipe.pk).exists():
                ingredient = ingredient_unit.ingredient
                pk = (IngredientUnit.objects
                      .get(ingredient=ingredient, unit=ingredient.primary_unit)
                      .pk)
                factor = get_factor(ingredient_unit, ingredient.primary_unit)
                if pk not in totals:
                    totals[pk] = 0
                    new_primary.add(pk)
            else:
                pk = ingredient_unit.pk
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
        if not request.user.is_authenticated:
            return redirect(
                f'{reverse(settings.LOGIN_URL)}?next={request.path}'
            )
        if not (config.OURGROCERIES_USERNAME and
                config.OURGROCERIES_PASSWORD and
                config.OURGROCERIES_LIST):
            error = _('OurGroceries is not completely configured')

        if not error:
            dishes = Dishes.objects.get_or_create()[0]
            for recipe, qty in recipes:
                dishes.add(recipe.pk, f'{recipe} ({qty})')
                recipe.popularity += 1
                recipe.save()
            dishes.save()

            try:
                add_to_ourgroceries(ingredient_units, ingredient_sel)
                message = _('Items succesfully added to OurGroceries')
                recipes, ingredient_sel, ingredient_units = [], [], []
            except Exception:
                error = _('Encountered an error adding items to OurGroceries')
                tb = traceback.format_exc()
            else:
                request.session['cart'] = {}
                request.session['ingredient_sel'] = []
                request.session.save()

    return render(request, 'cart.html', context={
        'page': 'cart',
        'recipes': recipes,
        'ingredient_sel': ingredient_sel,
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
                    else f'{localize(total)}{ingredient_unit["unit"]}')
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
    s.post(OURGROCERIES_SIGNIN_URL, data={
        'emailAddress': config.OURGROCERIES_USERNAME,
        'action': 'sign-in',
        'password': config.OURGROCERIES_PASSWORD,
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
            f'No shopping list named {config.OURGROCERIES_LIST} '
            f'on OurGroceries for {config.OURGROCERIES_USERNAME}')
    s.post(OURGROCERIES_LIST_URL, data=json.dumps({
        'command': 'importItems',
        'files': [f.read()],
        'listId': list_id,
        'preview': False,
        'teamId': team_id,
    }), headers={
        'Referer': f'{OURGROCERIES_LIST_URL}list/{list_id}',
        'Origin': 'https://www.ourgroceries.com',
        'Accept': 'application/json, text/javascript, */*',
        'X-Requested-With': 'XMLHttpRequest',
        'Host': 'www.ourgroceries.com',
        'Content-Type': 'application/json; charset=UTF-8',
    }).raise_for_status()


def menu_today(request):
    today = date.today()
    return redirect(
        reverse('menu', args=[today.year, int(today.strftime('%V'))]))


def add_to_dishes(request):
    pk = request.POST['pk']
    dish = request.POST['dish']
    source = request.POST.get('source')
    if source is not None:
        year, week, day, meal = source.split('_')
        menu = Menu.objects.get(year=year, week=week)
        menu.remove(day, meal, pk, dish)
    dishes = Dishes.objects.get_or_create()[0]
    dishes.add(pk, dish)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def del_from_dishes(request):
    pk = request.POST['pk']
    dish = request.POST['dish']
    dishes = Dishes.objects.get_or_create()[0]
    dishes.remove(pk, dish)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def add_to_menu(request, year, week, day, meal):
    pk = request.POST['pk']
    dish = request.POST['dish']
    source = request.POST['source']
    menu = Menu.objects.get_or_create(year=year, week=week)[0]
    menu.add(day, meal, pk, dish)
    if source == 'dishes':
        dishes = Dishes.objects.get_or_create()[0]
        dishes.remove(pk, dish)
    else:
        day, meal = source.split('_')
        menu.remove(day, meal, pk, dish)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def del_from_menu(request, year, week, day, meal):
    pk = request.POST['pk']
    dish = request.POST['dish']
    menu = Menu.objects.get_or_create(year=year, week=week)[0]
    menu.remove(day, meal, pk, dish)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def change_note(request, year, week, day, meal):
    note = request.POST['note']
    menu = Menu.objects.get_or_create(year=year, week=week)[0]
    menu.note(day, meal, note)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def menu(request, year, week):
    start = datetime.strptime(f'{year} {week} 1', '%G %V %u').date()
    end = datetime.strptime(f'{year} {week} 7', '%G %V %u').date()
    prev_week = start - timedelta(days=7)
    next_week = start + timedelta(days=7)
    prev = reverse(
        'menu', args=[prev_week.year, int(prev_week.strftime('%V'))])
    next = reverse(
        'menu', args=[next_week.year, int(next_week.strftime('%V'))])
    try:
        menu = Menu.objects.get(year=year, week=week)
    except Menu.DoesNotExist:
        try:
            template = MenuTemplate.objects.get(active=True).template
        except MenuTemplate.DoesNotExist:
            menu = None
        else:
            template['year'] = year
            template['week'] = week
            menu = Menu.objects.create(**template)
    dishes = Dishes.objects.get_or_create()[0]
    return render(request, 'menu.html', {
        'page': 'menu',
        'day_of_week': DAYS_OF_THE_WEEK[date.today().weekday()],
        'days': DAYS_OF_THE_WEEK,
        'meals': ['lunch', 'dinner'],
        'dishes': dishes.list,
        'menu': menu,
        'year': year,
        'week': week,
        'start': start,
        'end': end,
        'prev': prev,
        'next': next,
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
            return f'{self.name} ({self.unit})'

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
