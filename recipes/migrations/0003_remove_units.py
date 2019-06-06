from django.db import migrations


UNITS = [
    ('W', 'tsp'),
    ('W', 'tbsp'),
    ('W', 'cup'),
]


def remove_units(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')
    Ingredient = apps.get_model('recipes', 'Ingredient')

    for measured, name in UNITS:
        try:
            unit_from = Unit.objects.get(name=name, measured=measured)
            unit_to = Unit.objects.get(name=name, measured='V')
        except:
            continue
        Ingredient.objects.filter(unit=unit_from).update(unit=unit_to)
        unit_from.delete()


class Migration(migrations.Migration):

    dependencies = [('recipes', '0002_add_units')]

    operations = [migrations.RunPython(remove_units)]
