from django.db import migrations


UNITS = [
    'pc',

    'g',
    'kg',
    'lb',
    'oz',

    'ml',
    'cl',
    'dl',
    'l',
    'tsp',
    'tbsp',
    'fl oz',
    'cup',

    'cm',
    'in',
]


def add_order_to_units(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')

    for index, name in enumerate(UNITS, 1):
        try:
            unit = Unit.objects.get(name=name)
            unit.order = index
            unit.save()
        except Unit.DoesNotExist:
            pass


def remove_order(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')
    Unit.objects.all().update(order=0)


class Migration(migrations.Migration):

    dependencies = [('recipes', '0006_add_unit_order')]

    operations = [migrations.RunPython(add_order_to_units, remove_order)]
