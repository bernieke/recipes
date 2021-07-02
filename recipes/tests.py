import re

from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate

from .models import (
    get_factor,
    Category,
    Ingredient,
    IngredientInRecipe,
    IngredientUnit,
    Recipe,
    Tag,
    Unit,
    UnitConversion,
)


class FactorTestCase(TestCase):

    def setUp(self):
        self.tbsp, _ = Unit.objects.get_or_create(name='tbsp')
        self.tsp, _ = Unit.objects.get_or_create(name='tsp')
        self.ml, _ = Unit.objects.get_or_create(name='ml')
        self.l, _ = Unit.objects.get_or_create(name='l')
        self.g, _ = Unit.objects.get_or_create(name='g')
        self.kg, _ = Unit.objects.get_or_create(name='kg')
        self.inch, _ = Unit.objects.get_or_create(name='in')
        self.cm, _ = Unit.objects.get_or_create(name='cm')
        self.x, _ = Unit.objects.get_or_create(name='x')
        self.y, _ = Unit.objects.get_or_create(name='y')
        self.ingredient = Ingredient.objects.create(
            name='ingredient', primary_unit=self.ml)
        self.ingredient_ml = IngredientUnit.objects.get(
            ingredient=self.ingredient, unit=self.ml)
        self.ingredient_tbsp = IngredientUnit.objects.create(
            ingredient=self.ingredient, unit=self.tbsp, factor=Decimal('15'))
        self.ingredient_g = IngredientUnit.objects.create(
            ingredient=self.ingredient, unit=self.g, factor=Decimal('10'))

    def test_no_factor(self):
        self.assertEqual(get_factor(self.ingredient_ml, self.ml), Decimal('1'))

    def test_from_primary(self):
        self.assertEqual(
            get_factor(self.ingredient_ml, self.g), Decimal('0.1'))

    def test_to_primary(self):
        self.assertEqual(
            get_factor(self.ingredient_g, self.ml), Decimal('10'))

    def test_between(self):
        self.assertEqual(
            get_factor(self.ingredient_tbsp, self.g), Decimal('1.5'))

    def test_unit_conversion(self):
        ingredient_in = IngredientUnit.objects.create(
            ingredient=self.ingredient, unit=self.inch, factor=Decimal('10'))
        try:
            self.assertEqual(
                get_factor(ingredient_in, self.cm), Decimal('2.54'))
        finally:
            ingredient_in.delete()

    def test_reverse_unit_conversion(self):
        self.assertEqual(
            get_factor(self.ingredient_ml, self.l), Decimal('0.001'))

    def test_common_to_unit_conversion(self):
        self.assertEqual(
            get_factor(self.ingredient_tbsp, self.tsp), Decimal('3'))

    def test_common_from_unit_conversion(self):
        uc = UnitConversion.objects.create(
            from_unit=self.l, to_unit=self.kg, factor=Decimal('2'))
        try:
            self.assertEqual(
                get_factor(self.ingredient_ml, self.kg), Decimal('0.002'))
        finally:
            uc.delete()

    def test_diagonal_from_conversion(self):
        ingredient_in = IngredientUnit.objects.create(
            ingredient=self.ingredient, unit=self.inch, factor=Decimal('10'))
        uc = UnitConversion.objects.create(
            from_unit=self.cm, to_unit=self.x, factor=Decimal('2'))
        try:
            self.assertEqual(
                get_factor(ingredient_in, self.x), Decimal('5.08'))
        finally:
            ingredient_in.delete()
            uc.delete()

    def test_diagonal_to_conversion(self):
        ingredient_y = IngredientUnit.objects.create(
            ingredient=self.ingredient, unit=self.y, factor=Decimal('10'))
        uc1 = UnitConversion.objects.create(
            from_unit=self.x, to_unit=self.inch, factor=0.5)
        uc2 = UnitConversion.objects.create(
            from_unit=self.inch, to_unit=self.y, factor=0.25)
        try:
            self.assertEqual(
                get_factor(ingredient_y, self.x), Decimal('8'))
        finally:
            ingredient_y.delete()
            uc1.delete()
            uc2.delete()


class RecipesTestCase(TestCase):

    def model_to_cart(self, ingredient_unit, total):
        ingredient = ingredient_unit.ingredient
        category = ingredient.category
        unit = ingredient_unit.unit
        return [{
            'pk': ingredient_unit.pk,
            'name': ingredient.display_name,
            'category': category.name,
            'unit': unit.name,
            'unit_pk': unit.pk,
        }, Decimal(total)]

    def setUp(self):
        activate('en')
        self.client = Client()
        self.cat1 = Category.objects.create(name='cat1', order=1)
        self.cat2 = Category.objects.create(name='cat2', order=2)
        self.tag1 = Tag.objects.create(name='tag1', order=1)
        self.tag2 = Tag.objects.create(name='tag2', order=2)
        self.pc, _ = Unit.objects.get_or_create(name='pc')
        self.ts, _ = Unit.objects.get_or_create(name='ts')
        self.g, _ = Unit.objects.get_or_create(name='g')
        self.ingredient1 = Ingredient.objects.create(
            name='ingredient1', category=self.cat1)
        self.ingredient1pc = IngredientUnit.objects.create(
            ingredient=self.ingredient1, unit=self.pc)
        self.ingredient2 = Ingredient.objects.create(
            name='ingredient2', category=self.cat2)
        self.ingredient2ts = IngredientUnit.objects.create(
            ingredient=self.ingredient2, unit=self.ts)
        self.ingredient2g = IngredientUnit.objects.create(
            ingredient=self.ingredient2, unit=self.g)
        self.recipe1 = Recipe.objects.create(
            title='recipe1', recipe='Preparation recipe1')
        self.recipe2 = Recipe.objects.create(
            title='recipe2', recipe='Preparation recipe2')
        self.recipe1.tags.add(self.tag1)
        self.recipe1.tags.add(self.tag2)
        self.recipe2.tags.add(self.tag2)
        self.iir1_1 = IngredientInRecipe.objects.create(
            recipe=self.recipe1, ingredient_unit=self.ingredient1pc,
            amount=Decimal('3'), order=1)
        self.iir1_2ts = IngredientInRecipe.objects.create(
            recipe=self.recipe1, ingredient_unit=self.ingredient2ts,
            amount=Decimal('2'), order=2)
        self.iir2_1 = IngredientInRecipe.objects.create(
            recipe=self.recipe2, ingredient_unit=self.ingredient1pc,
            amount=Decimal('2'), order=1)
        self.iir2_2g = IngredientInRecipe.objects.create(
            recipe=self.recipe2, ingredient_unit=self.ingredient2g,
            amount=Decimal('1'), order=2)

    def test_index(self):
        # Index
        ctx = self.client.get(reverse('index'), follow=True).context
        self.assertEqual(ctx['page'], 'index')
        self.assertEqual(list(ctx['tags']), [self.tag1, self.tag2])
        self.assertEqual(ctx['selected_tag'], None)
        self.assertEqual(list(ctx['recipes']), [self.recipe1, self.recipe2])

        # Tag
        ctx = self.client.get(reverse('tag', args=[self.tag2.pk])).context
        self.assertEqual(ctx['selected_tag'], self.tag2)
        self.assertEqual(list(ctx['recipes']), [self.recipe1, self.recipe2])

    def test_order(self):
        self.tag1.order = 3
        self.tag1.save()
        self.recipe1.title = 'z'
        self.recipe1.save()
        ingredient_in_recipe = IngredientInRecipe.objects.first()
        ingredient_in_recipe.order = 3
        ingredient_in_recipe.save()
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe2.pk]))
        self.cat1.order = 3
        self.cat1.save()

        ctx = self.client.get(
            reverse('index') + '?order=title', follow=True).context
        # tag order
        self.assertEqual(list(ctx['tags']), [self.tag2, self.tag1])
        # recipe order by title on index
        self.assertEqual(list(ctx['recipes']), [self.recipe2, self.recipe1])

        ctx = self.client.get(
            reverse('recipe', args=[self.recipe1.pk])).context
        # ingredient in recipe order
        self.assertEqual(list(ctx['ingredient_units']),
                         [self.iir1_2ts, self.iir1_1])

        ctx = self.client.get(reverse('cart')).context
        # recipe order by title on cart
        recipes = [(self.recipe2, Decimal(1)), (self.recipe1, Decimal(2))]
        self.assertEqual(ctx['recipes'], recipes)
        # ingredient cart order by category
        ingredient_units = [self.model_to_cart(self.ingredient2ts, 4),
                            self.model_to_cart(self.ingredient2g, 1),
                            self.model_to_cart(self.ingredient1pc, 8)]
        self.assertEqual(ctx['ingredient_units'], ingredient_units)

    def test_recipe(self):
        ctx = self.client.get(
            reverse('recipe', args=[self.recipe1.pk])).context
        self.assertEqual(ctx['page'], 'recipe')
        self.assertEqual(ctx['recipe'], self.recipe1)
        self.assertEqual(list(ctx['ingredient_units']),
                         [self.iir1_1, self.iir1_2ts])

    def test_cart(self):
        # Add to cart
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe2.pk]))
        ctx = self.client.get(reverse('cart')).context
        self.assertEqual(ctx['page'], 'cart')
        recipes = [(self.recipe1, Decimal(2)), (self.recipe2, Decimal(1))]
        self.assertEqual(ctx['recipes'], recipes)
        ingredient_units = [self.model_to_cart(self.ingredient1pc, 8),
                            self.model_to_cart(self.ingredient2ts, 4),
                            self.model_to_cart(self.ingredient2g, 1)]
        self.assertEqual(ctx['ingredient_units'], ingredient_units)

        # Edit cart
        self.client.post(reverse('cart'), {
            'action': 'edit',
            'pk': self.recipe1.pk,
            'qty': 1.5,
        })
        ctx = self.client.get(reverse('cart')).context
        recipes = [(self.recipe1, Decimal(1.5)), (self.recipe2, Decimal(1))]
        self.assertEqual(ctx['recipes'], recipes)
        ingredient_units = [self.model_to_cart(self.ingredient1pc, 6.5),
                            self.model_to_cart(self.ingredient2ts, 3),
                            self.model_to_cart(self.ingredient2g, 1)]
        self.assertEqual(ctx['ingredient_units'], ingredient_units)

    def test_multiple_units(self):
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe2.pk]))

        self.ingredient2ts.factor = 10
        self.ingredient2ts.save()
        ctx = self.client.get(reverse('cart')).context
        ingredient_units = [self.model_to_cart(self.ingredient1pc, 5),
                            self.model_to_cart(self.ingredient2ts, 2),
                            self.model_to_cart(self.ingredient2g, 1)]
        self.assertEqual(ctx['ingredient_units'], ingredient_units)

        self.ingredient2.primary_unit = self.g
        self.ingredient2.save()
        ctx = self.client.get(reverse('cart')).context
        ingredient_units = [self.model_to_cart(self.ingredient1pc, 5),
                            self.model_to_cart(self.ingredient2g, 21)]
        self.assertEqual(ctx['ingredient_units'], ingredient_units)

    def test_localization(self):
        recipe = Recipe.objects.create(title='localization_test', recipe='')
        iir = IngredientInRecipe.objects.create(
            recipe=recipe, ingredient_unit=self.ingredient1pc, amount=1.5,
            order=1)
        self.client.get(reverse('add_to_cart', args=[recipe.pk]))
        self.client.post(reverse('cart'), {
            'action': 'edit',
            'pk': recipe.pk,
            'qty': 0.5,
        })

        # EN
        # On recipe page
        ctx = self.client.get(reverse('recipe', args=[recipe.pk])).context
        self.assertEqual(list(ctx['ingredient_units']), [iir])
        # On cart page
        ct = self.client.get(reverse('cart')).content.decode()
        self.assertIsNotNone(re.search(
            r'0.5\s+<a href="/en/recipe/\d+/"\s+class="text-body">'
            r'localization_test</a>', ct))
        self.assertTrue(re.search(r'ingredient1\s*\(0\.75\s*pc\)', ct))

        # NL
        activate('nl')
        # On recipe page
        ctx = self.client.get(reverse('recipe', args=[recipe.pk])).context
        self.assertEqual(list(ctx['ingredient_units']), [iir])
        # On cart page
        ct = self.client.get(reverse('cart')).content.decode()
        self.assertIsNotNone(re.search(
            r'0,5\s+<a href="/nl/recipe/\d+/"\s+class="text-body">'
            r'localization_test</a>', ct))
        self.assertTrue(re.search(r'ingredient1\s*\(0\,75\s*st\)', ct))
