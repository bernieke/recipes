from decimal import Context

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.formats import localize
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_markdown.models import MarkdownField


def fahrenheit_to_celcius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


def normalize(d):
    normalized = d.normalize(Context(settings.AMOUNT_PRECISION))
    threshold = 10 ** settings.AMOUNT_PRECISION
    return int(normalized) if d >= threshold else normalized


class Unit(models.Model):
    name = models.CharField(max_length=16, verbose_name=_('name'))
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False,
        verbose_name=_('order'))

    class Meta:
        ordering = ('order', 'name')
        verbose_name = _('unit')
        verbose_name_plural = _('units')

    def __str__(self):
        return self.name


class UnitConversion(models.Model):
    from_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='from_unit',
        verbose_name=_('from unit'))
    to_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='to_unit',
        verbose_name=_('to unit'))
    factor = models.DecimalField(
        max_digits=7, decimal_places=3, verbose_name=_('factor'))

    class Meta:
        ordering = ('from_unit', 'to_unit')
        unique_together = [['from_unit', 'to_unit']]
        verbose_name = _('unit conversion')
        verbose_name_plural = _('unit conversions')

    def __str__(self):
        return '1 {} = {} {}'.format(
            self.from_unit, localize(self.factor), self.to_unit)


class IngredientUnit(models.Model):
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    unit = models.ForeignKey(
        'Unit', on_delete=models.PROTECT, verbose_name=_('unit'))
    factor = models.DecimalField(
        max_digits=7, decimal_places=3, blank=True, null=True, default=None,
        verbose_name=_('factor'))

    class Meta:
        unique_together = [['ingredient', 'unit']]
        verbose_name = _('unit')
        verbose_name_plural = _('units')

    def __str__(self):
        return '{} ({})'.format(self.ingredient.name, self.unit.name)


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('name'))
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False,
        verbose_name=_('order'))

    class Meta:
        ordering = ('order', 'name')
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True, verbose_name=_('name'))
    order = models.PositiveSmallIntegerField(
        default=32767, db_index=True, blank=False, null=False,
        verbose_name=_('order'))
    break_after = models.BooleanField(default=False)

    class Meta:
        ordering = ('order', 'name')
        verbose_name = _('tag')
        verbose_name_plural = _('tags')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[str(self.id)])

    def recipes(self):
        return mark_safe('<br>'.join(
            ['<a href="{}"><b>{}</b></a>'.format(
                reverse('admin:recipes_recipe_change', args=[recipe.pk]),
                recipe.title)
             for recipe in self.recipe_set.all()]))

    recipes.short_description = _('recipes')


class Ingredient(models.Model):
    name = models.CharField(
        max_length=254, blank=True, unique=True, verbose_name=_('name'))
    primary_unit = models.ForeignKey(
        'Unit', on_delete=models.PROTECT, null=True, blank=True,
        default=None, related_name='primary_unit',
        verbose_name=_('primary unit'))
    category = models.ForeignKey(
        'Category', on_delete=models.PROTECT, null=True, blank=True,
        verbose_name=_('category'))

    class Meta:
        ordering = ('name',)
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')

    def __str__(self):
        if self.primary_unit:
            return '{} ({})'.format(self.name, self.primary_unit.name)
        else:
            return self.name

    def units(self):
        return ', '.join(self.ingredientunit_set.all()
                         .values_list('unit__name', flat=True))

    def recipes(self):
        ingredient_in_recipes = (IngredientInRecipe.objects
                                 .filter(ingredient_unit__ingredient=self))
        return mark_safe('<br>'.join(
            ['{} {} in <a href="{}"><b>{}</b></a>'.format(
                localize(normalize(ingredient_in_recipe.amount)),
                ingredient_in_recipe.ingredient_unit.unit.name,
                reverse('admin:recipes_recipe_change',
                        args=[ingredient_in_recipe.recipe.pk]),
                ingredient_in_recipe.recipe.title)
             for ingredient_in_recipe in ingredient_in_recipes]))

    units.short_description = _('units')
    recipes.short_description = _('recipes')


class Alias(models.Model):
    name = models.CharField(
        max_length=254, unique=True, verbose_name=_('name'))
    ingredient = models.ForeignKey(
        'Ingredient', on_delete=models.CASCADE, verbose_name=_('ingredient'))

    class Meta:
        ordering = ('name',)
        verbose_name = _('alias')
        verbose_name_plural = _('aliases')

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(
        max_length=254, unique=True, verbose_name=_('title'))
    tags = models.ManyToManyField('Tag', blank=True, verbose_name=_('tags'))
    ingredient_units = models.ManyToManyField(
        'IngredientUnit', through='IngredientInRecipe', blank=True,
        verbose_name=_('ingredients'))
    recipe = MarkdownField(blank=True, verbose_name=_('recipe'))

    class Meta:
        ordering = ('title',)
        verbose_name = _('recipe')
        verbose_name_plural = _('recipes')

    def __str__(self):
        return self.title

    def tag_list(self):
        return ', '.join(self.tags.all().values_list('name', flat=True))

    def get_absolute_url(self):
        return reverse('recipe', args=[str(self.id)])

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', args=[str(self.id)])

    tag_list.short_description = _('tags')


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name=_('recipe'))
    ingredient_unit = models.ForeignKey(
        IngredientUnit, on_delete=models.PROTECT, verbose_name=_('ingredient'))
    amount = models.DecimalField(
        max_digits=7, decimal_places=3, verbose_name=_('amount'))
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False,
        verbose_name=_('order'))

    class Meta:
        ordering = ('order',)
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')

    def __str__(self):
        if not self.ingredient_unit.ingredient.name:
            return ''
        if not self.amount:
            return self.ingredient_unit.ingredient.name
        return '{} {} {}'.format(
            localize(normalize(self.amount)),
            self.ingredient_unit.unit.name,
            self.ingredient_unit.ingredient.name)
