import os.path

from django.db import models


def image_filename(instance, filename):
    return instance.title + os.path.splitext(filename)[1]


class Unit(models.Model):
    name = models.CharField(max_length=16)


class UnitConversion(models.Model):
    unit_from = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='unit_from')
    unit_to = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='unit_to')
    factor = models.DecimalField(max_digits=7, decimal_places=3)


class Tag(models.Model):
    name = models.CharField(max_length=64)


class Ingredient(models.Model):
    name = models.CharField(max_length=254)
    unit = models.ForeignKey('Unit', on_delete=models.PROTECT)


class Recipe(models.Model):
    title = models.CharField(max_length=254)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField(
        'Ingredient', through='IngredientInRecipe')
    recipe = models.TextField()
    image = models.ImageField(image_filename)


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.SmallIntegerField()
    order = models.SmallIntegerField()
