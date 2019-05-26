import os.path

from django.db import models


MEASURED = [
    ('W', 'weight'),
    ('V', 'volume'),
]


def fahrenheit_to_celcius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


def image_filename(instance, filename):
    return instance.title + os.path.splitext(filename)[1]


class Unit(models.Model):
    name = models.CharField(max_length=16)
    measured = models.CharField(choices=MEASURED, max_length=1)

    class Meta:
        ordering = ('name', 'measured')
        unique_together = [['name', 'measured']]

    def __str__(self):
        return '{} [{}]'.format(self.name, self.measured)


class UnitConversion(models.Model):
    unit_from = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='unit_from')
    unit_to = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='unit_to')
    factor = models.DecimalField(max_digits=7, decimal_places=3)

    class Meta:
        ordering = ('unit_from', 'unit_to')
        unique_together = [['unit_from', 'unit_to']]

    def __str__(self):
        return '1 {} = {} {}'.format(self.unit_from, self.factor, self.unit_to)


class Tag(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=254)
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT)

    class Meta:
        ordering = ('name', 'unit')
        unique_together = [['name', 'unit']]

    def __str__(self):
        return '{} ({})'.format(self.name, self.unit)


class Recipe(models.Model):
    title = models.CharField(max_length=254, unique=True)
    tags = models.ManyToManyField('Tag', blank=True)
    ingredients = models.ManyToManyField(
        'Ingredient', through='IngredientInRecipe', blank=True)
    recipe = models.TextField(blank=True)
    image = models.ImageField(upload_to=image_filename, blank=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False)

    class Meta:
        ordering = ('order',)
        verbose_name = 'Ingredient'
