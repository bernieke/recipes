import uuid

from decimal import Context, Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
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


def get_factor(ingredient_unit, unit):
    if unit == ingredient_unit.unit:
        return 1

    else:
        factor = None

        # First see if we can convert through the ingredient units
        try:
            if ingredient_unit.factor:
                factor1 = ingredient_unit.factor
            else:
                factor1 = Decimal(1)
            factor2 = (ingredient_unit
                       .ingredient
                       .ingredientunit_set
                       .get(unit=unit)).factor
            if factor2:
                factor = factor1 * (1 / factor2)
            else:
                factor = factor1
        except IngredientUnit.DoesNotExist:
            pass

        # Then try the unit conversion
        if factor is None:
            try:
                factor = UnitConversion.objects.get(
                    from_unit=ingredient_unit.unit, to_unit=unit).factor
            except UnitConversion.DoesNotExist:
                pass

        # And the reverse unit conversion
        if factor is None:
            try:
                factor = 1 / UnitConversion.objects.get(
                    from_unit=unit, to_unit=ingredient_unit.unit).factor
            except UnitConversion.DoesNotExist:
                pass

        # Now look for a common to_unit
        if factor is None:
            sub = UnitConversion.objects.filter(from_unit=unit)
            qs = UnitConversion.objects.filter(
                from_unit=ingredient_unit.unit,
                to_unit__in=models.Subquery(sub.values('to_unit')))
            first = qs.first()
            if first:
                second = sub.filter(to_unit=first.to_unit).first()
                factor = first.factor * (1 / second.factor)

        # Or a common from_unit
        if factor is None:
            sub = UnitConversion.objects.filter(to_unit=ingredient_unit.unit)
            qs = UnitConversion.objects.filter(
                from_unit__in=models.Subquery(sub.values('from_unit')),
                to_unit=unit)
            first = qs.first()
            if first:
                second = sub.filter(from_unit=first.from_unit).first()
                factor = first.factor * (1 / second.factor)

        # Finally try a diagonal match through the from_unit
        if factor is None:
            sub = UnitConversion.objects.filter(to_unit=unit)
            qs = UnitConversion.objects.filter(
                from_unit=ingredient_unit.unit,
                to_unit__in=models.Subquery(sub.values('from_unit')))
            first = qs.first()
            if first:
                second = sub.filter(from_unit=first.to_unit).first()
                factor = first.factor * second.factor

        # And through the to_unit
        if factor is None:
            sub = UnitConversion.objects.filter(from_unit=unit)
            qs = UnitConversion.objects.filter(
                from_unit__in=models.Subquery(sub.values('to_unit')),
                to_unit=ingredient_unit.unit)
            first = qs.first()
            if first:
                second = sub.filter(to_unit=first.from_unit).first()
                factor = 1 / (first.factor * second.factor)

        return factor


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
        return '{} ({})'.format(self.ingredient.display_name, self.unit.name)


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

    @property
    def display_name(self):
        if ', ' in self.name:
            try:
                return self.alias_set.first().name
            except AttributeError:
                parts = self.name.split(', ')
                parts.reverse()
                return ' '.join(parts)
        else:
            return self.name

    def __str__(self):
        if self.primary_unit:
            return '{} ({})'.format(self.display_name, self.primary_unit.name)
        else:
            return self.display_name

    def units(self):
        return mark_safe(', '.join(
            (['<b>{}</b>'.format(self.primary_unit)]
             if self.primary_unit else []) +
            list(self.ingredientunit_set.all()
                 .exclude(unit=self.primary_unit)
                 .values_list('unit__name', flat=True))))

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
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False,
        verbose_name=_('order'))

    class Meta:
        ordering = ('order',)
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
            return self.ingredient_unit.ingredient.display_name
        return '{} {} {}'.format(
            localize(normalize(self.amount)),
            self.ingredient_unit.unit.name,
            self.ingredient_unit.ingredient.display_name)


class PreventOverwriteMixin(models.Model):
    last_change_id = models.UUIDField(default=uuid.uuid4)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        try:
            last = self.__class__.objects.get(pk=self.pk)
            if not str(last.last_change_id) == str(self.last_change_id):
                raise ValidationError(
                    _('The menu has already been changed '
                      'in a different location, please try again'))
        except self.DoesNotExist:
            pass
        self.last_change_id = uuid.uuid4()
        return super().save(*args, **kwargs)


class Dishes(PreventOverwriteMixin):
    dishes = models.TextField(blank=True)


class Menu(PreventOverwriteMixin):
    monday_lunch_dishes = models.TextField(blank=True)
    monday_dinner_dishes = models.TextField(blank=True)
    tuesday_lunch_dishes = models.TextField(blank=True)
    tuesday_dinner_dishes = models.TextField(blank=True)
    wednesday_lunch_dishes = models.TextField(blank=True)
    wednesday_dinner_dishes = models.TextField(blank=True)
    thursday_lunch_dishes = models.TextField(blank=True)
    thursday_dinner_dishes = models.TextField(blank=True)
    friday_lunch_dishes = models.TextField(blank=True)
    friday_dinner_dishes = models.TextField(blank=True)
    saturday_lunch_dishes = models.TextField(blank=True)
    saturday_dinner_dishes = models.TextField(blank=True)
    sunday_lunch_dishes = models.TextField(blank=True)
    sunday_dinner_dishes = models.TextField(blank=True)

    monday_lunch_note = models.TextField(blank=True)
    monday_dinner_note = models.TextField(blank=True)
    tuesday_lunch_note = models.TextField(blank=True)
    tuesday_dinner_note = models.TextField(blank=True)
    wednesday_lunch_note = models.TextField(blank=True)
    wednesday_dinner_note = models.TextField(blank=True)
    thursday_lunch_note = models.TextField(blank=True)
    thursday_dinner_note = models.TextField(blank=True)
    friday_lunch_note = models.TextField(blank=True)
    friday_dinner_note = models.TextField(blank=True)
    saturday_lunch_note = models.TextField(blank=True)
    saturday_dinner_note = models.TextField(blank=True)
    sunday_lunch_note = models.TextField(blank=True)
    sunday_dinner_note = models.TextField(blank=True)


def create_ingredient_unit_for_primary_unit(sender, instance, **kwargs):
    if instance.primary_unit:
        IngredientUnit.objects.update_or_create(
            ingredient=instance, unit=instance.primary_unit, factor=None)


models.signals.post_save.connect(
    create_ingredient_unit_for_primary_unit, sender=Ingredient)
