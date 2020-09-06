import re

from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate

from .models import (
    Category, Unit, Tag, Ingredient, IngredientUnit, IngredientInRecipe, Recipe
)


class RecipesTestCase(TestCase):

    def model_to_cart(self, ingredient_unit, total):
        ingredient = ingredient_unit.ingredient
        category = ingredient.category
        unit = ingredient_unit.unit
        return [{
            'pk': ingredient_unit.pk,
            'ingredient__name': ingredient.name,
            'ingredient__category__name': category.name,
            'unit__pk': unit.pk,
            'unit__name': unit.name,
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

        ctx = self.client.get(reverse('index'), follow=True).context
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
        self.assertTrue('0.5 localization_test' in ct)
        self.assertTrue(re.search(r'ingredient1\s*\(0\.75\s*pc\)', ct))

        # NL
        activate('nl')
        # On recipe page
        ctx = self.client.get(reverse('recipe', args=[recipe.pk])).context
        self.assertEqual(list(ctx['ingredient_units']), [iir])
        # On cart page
        ct = self.client.get(reverse('cart')).content.decode()
        self.assertTrue('0,5 localization_test' in ct)
        self.assertTrue(re.search(r'ingredient1\s*\(0\,75\s*pc\)', ct))
