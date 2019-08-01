from decimal import Context

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.formats import localize
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


class Ingredient(models.Model):
    name = models.CharField(max_length=254, blank=True, verbose_name=_('name'))
    unit = models.ForeignKey(
        'Unit', on_delete=models.PROTECT, verbose_name=_('unit'))
    category = models.ForeignKey(
        'Category', on_delete=models.PROTECT, null=True, blank=True,
        verbose_name=_('category'))

    class Meta:
        ordering = ('name', 'unit')
        unique_together = [['name', 'unit']]
        verbose_name = _('ingredient')
        verbose_name_plural = _('ingredients')

    def __str__(self):
        return '{} ({})'.format(self.name, self.unit)


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
    ingredients = models.ManyToManyField(
        'Ingredient', through='IngredientInRecipe', blank=True,
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
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, verbose_name=_('ingredient'))
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
        if not self.ingredient.name:
            return ''
        if not self.amount:
            return self.ingredient.name
        return '{}{} {}'.format(
            localize(normalize(self.amount)),
            self.ingredient.unit.name,
            self.ingredient.name)
