import re

from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.utils.translation import activate

from .models import Category, Unit, Tag, Ingredient, IngredientInRecipe, Recipe


class RecipesTestCase(TestCase):

    def ingredient_to_recipe(self, ingredient, amount):
        return '{}{} {}'.format(
            amount, ingredient.unit.name, ingredient.name)

    def ingredient_to_cart(self, ingredient, total):
        return [{
            'ingredient__pk': ingredient.pk,
            'ingredient__name': ingredient.name,
            'ingredient__category__name': ingredient.category.name,
            'ingredient__unit__pk': ingredient.unit.pk,
            'ingredient__unit__name': ingredient.unit.name,
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
            name='ingredient1', unit=self.pc, category=self.cat1)
        self.ingredient2ts = Ingredient.objects.create(
            name='ingredient2ts', unit=self.ts, category=self.cat2)
        self.ingredient2g = Ingredient.objects.create(
            name='ingredient2g', unit=self.g, category=self.cat2)
        self.recipe1 = Recipe.objects.create(
            title='recipe1', recipe='Preparation recipe1')
        self.recipe2 = Recipe.objects.create(
            title='recipe2', recipe='Preparation recipe2')
        self.recipe1.tags.add(self.tag1)
        self.recipe1.tags.add(self.tag2)
        self.recipe2.tags.add(self.tag2)
        IngredientInRecipe.objects.create(
            recipe=self.recipe1, ingredient=self.ingredient1,
            amount=3, order=1)
        IngredientInRecipe.objects.create(
            recipe=self.recipe1, ingredient=self.ingredient2ts,
            amount=2, order=2)
        IngredientInRecipe.objects.create(
            recipe=self.recipe2, ingredient=self.ingredient1,
            amount=2, order=1)
        IngredientInRecipe.objects.create(
            recipe=self.recipe2, ingredient=self.ingredient2g,
            amount=1, order=2)

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
        self.assertEqual(ctx['ingredients'], [
            self.ingredient_to_recipe(self.ingredient2ts, 2),
            self.ingredient_to_recipe(self.ingredient1, 3)])

        ctx = self.client.get(reverse('cart')).context
        # recipe order by title on cart
        recipes = [(self.recipe2, Decimal(1)), (self.recipe1, Decimal(2))]
        self.assertEqual(ctx['recipes'], recipes)
        # ingredient cart order by category
        ingredients = [self.ingredient_to_cart(self.ingredient2ts, 4),
                       self.ingredient_to_cart(self.ingredient2g, 1),
                       self.ingredient_to_cart(self.ingredient1, 8)]
        self.assertEqual(ctx['ingredients'], ingredients)

    def test_recipe(self):
        ctx = self.client.get(
            reverse('recipe', args=[self.recipe1.pk])).context
        self.assertEqual(ctx['page'], 'recipe')
        self.assertEqual(ctx['recipe'], self.recipe1)
        self.assertEqual(ctx['ingredients'], [
            self.ingredient_to_recipe(self.ingredient1, 3),
            self.ingredient_to_recipe(self.ingredient2ts, 2)])

    def test_cart(self):
        # Add to cart
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe1.pk]))
        self.client.get(reverse('add_to_cart', args=[self.recipe2.pk]))
        ctx = self.client.get(reverse('cart')).context
        self.assertEqual(ctx['page'], 'cart')
        recipes = [(self.recipe1, Decimal(2)), (self.recipe2, Decimal(1))]
        self.assertEqual(ctx['recipes'], recipes)
        ingredients = [self.ingredient_to_cart(self.ingredient1, 8),
                       self.ingredient_to_cart(self.ingredient2ts, 4),
                       self.ingredient_to_cart(self.ingredient2g, 1)]
        self.assertEqual(ctx['ingredients'], ingredients)

        # Edit cart
        self.client.post(reverse('cart'), {
            'action': 'edit',
            'pk': self.recipe1.pk,
            'qty': 1.5,
        })
        ctx = self.client.get(reverse('cart')).context
        recipes = [(self.recipe1, Decimal(1.5)), (self.recipe2, Decimal(1))]
        self.assertEqual(ctx['recipes'], recipes)
        ingredients = [self.ingredient_to_cart(self.ingredient1, 6.5),
                       self.ingredient_to_cart(self.ingredient2ts, 3),
                       self.ingredient_to_cart(self.ingredient2g, 1)]
        self.assertEqual(ctx['ingredients'], ingredients)

    def test_localization(self):
        recipe = Recipe.objects.create(title='localization_test', recipe='')
        IngredientInRecipe.objects.create(
            recipe=recipe, ingredient=self.ingredient1, amount=1.5, order=1)
        self.client.get(reverse('add_to_cart', args=[recipe.pk]))
        self.client.post(reverse('cart'), {
            'action': 'edit',
            'pk': recipe.pk,
            'qty': 0.5,
        })

        # EN
        # On recipe page
        ctx = self.client.get(reverse('recipe', args=[recipe.pk])).context
        self.assertEqual(ctx['ingredients'], [
            self.ingredient_to_recipe(self.ingredient1, '1.5')])
        # On cart page
        ct = self.client.get(reverse('cart')).content.decode()
        self.assertTrue('0.5 localization_test' in ct)
        self.assertTrue(re.search(r'ingredient1\s*\(0\.75\s*pc\)', ct))

        # NL
        activate('nl')
        # On recipe page
        ctx = self.client.get(reverse('recipe', args=[recipe.pk])).context
        self.assertEqual(ctx['ingredients'], [
            self.ingredient_to_recipe(self.ingredient1, '1,5')])
        # On cart page
        ct = self.client.get(reverse('cart')).content.decode()
        self.assertTrue('0,5 localization_test' in ct)
        self.assertTrue(re.search(r'ingredient1\s*\(0\,75\s*pc\)', ct))
