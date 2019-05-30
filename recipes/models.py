from django.db import models
from django.urls import reverse


MEASURED = [
    ('', 'piece'),
    ('W', 'weight'),
    ('V', 'volume'),
    ('L', 'length'),
]


def fahrenheit_to_celcius(fahrenheit):
    return (fahrenheit - 32) * 5 / 9


class Unit(models.Model):
    name = models.CharField(max_length=16)
    measured = models.CharField(choices=MEASURED, max_length=1)

    class Meta:
        ordering = ('name', 'measured')
        unique_together = [['name', 'measured']]

    def __str__(self):
        if self.measured:
            return '{} [{}]'.format(self.name, self.measured)
        else:
            return self.name


class UnitConversion(models.Model):
    from_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='from_unit')
    to_unit = models.ForeignKey(
        'Unit', on_delete=models.CASCADE, related_name='to_unit')
    factor = models.DecimalField(max_digits=7, decimal_places=3)

    class Meta:
        ordering = ('from_unit', 'to_unit')
        unique_together = [['from_unit', 'to_unit']]

    def __str__(self):
        return '1 {} = {} {}'.format(self.from_unit, self.factor, self.to_unit)


class Category(models.Model):
    name = models.CharField(max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)
    order = models.PositiveSmallIntegerField(
        default=32767, db_index=True, blank=False, null=False)

    class Meta:
        ordering = ('order', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tag', args=[str(self.id)])


class Ingredient(models.Model):
    name = models.CharField(max_length=254)
    unit = models.ForeignKey(
        'Unit', on_delete=models.PROTECT, default=None, null=True)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)

    class Meta:
        ordering = ('name', 'unit')
        unique_together = [['name', 'unit']]

    def __str__(self):
        return '{} ({})'.format(self.name, self.unit)


class Alias(models.Model):
    name = models.CharField(max_length=254, unique=True)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=254, unique=True)
    tags = models.ManyToManyField('Tag', blank=True)
    ingredients = models.ManyToManyField(
        'Ingredient', through='IngredientInRecipe', blank=True)
    recipe = models.TextField(blank=True)

    class Meta:
        ordering = ('title',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe', args=[str(self.id)])

    def get_add_to_cart_url(self):
        return reverse('add_to_cart', args=[str(self.id)])


class IngredientInRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    order = models.PositiveSmallIntegerField(
        default=0, db_index=True, blank=False, null=False)

    class Meta:
        ordering = ('order',)
        verbose_name = 'Ingredient'
