from django.db import migrations


def migrate(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    Alias = apps.get_model('recipes', 'Alias')
    IngredientUnit = apps.get_model('recipes', 'IngredientUnit')
    IngredientInRecipe = apps.get_model('recipes', 'IngredientInRecipe')

    ingredients = {}
    for ingredient in Ingredient.objects.all():
        first = ingredient.name not in ingredients
        if first:
            ingredients[ingredient.name] = ingredient

        # Create IngredientUnit
        ingredient_unit = IngredientUnit.objects.create(
            ingredient=ingredients[ingredient.name], unit=ingredient.unit)

        # Update recipes
        (IngredientInRecipe.objects
         .filter(ingredient=ingredient)
         .update(ingredient=None, ingredient_unit=ingredient_unit))

        if not first:
            # Move any missing aliases
            existing_alias_names = (ingredients[ingredient.name].alias_set
                                    .all().values_list('name', flat=True))
            (Alias.objects
             .filter(ingredient=ingredient)
             .exclude(name__in=existing_alias_names)
             .update(ingredient=ingredients[ingredient.name]))

            # Delete double ingredient
            ingredient.delete()

    # Assign primary units where only one IngredientUnit exists
    for ingredient in Ingredient.objects.all():
        try:
            ingredient.primary_unit = ingredient.ingredientunit_set.get().unit
            ingredient.save()
        except IngredientUnit.MultipleObjectsReturned:
            pass


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_add_ingredient_unit'),
    ]

    operations = [
        migrations.RunPython(migrate),
    ]
