from django.db import migrations


UNITS = [
    ('W', 'g'),
    ('W', 'kg'),
    ('W', 'lb'),
    ('W', 'oz'),

    ('V', 'ml'),
    ('V', 'cl'),
    ('V', 'dl'),
    ('V', 'l'),

    ('W', 'tsp'),
    ('W', 'tbsp'),
    ('W', 'cup'),

    ('V', 'tsp'),
    ('V', 'tbsp'),
    ('V', 'oz'),
    ('V', 'cup'),

    ('W', 'st'),
]

UNIT_CONVERSIONS = [
    ('W', 'kg', 'g', '1000'),
    ('W', 'lb', 'g', '453.592'),
    ('W', 'oz', 'g', '28.35'),

    ('V', 'cl', 'ml', '10'),
    ('V', 'dl', 'ml', '100'),
    ('V', 'l', 'ml', '1000'),

    ('V', 'tsp', 'ml', '5'),
    ('V', 'tbsp', 'ml', '15'),
    ('V', 'oz', 'ml', '30'),
    ('V', 'cup', 'ml', '240'),
]


def create_units(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')
    UnitConversion = apps.get_model('recipes', 'UnitConversion')

    units = {}
    for measured, name in UNITS:
        units[(measured, name)] = Unit.objects.create(
            name=name, measured=measured)

    for measured, from_unit_name, to_unit_name, factor in UNIT_CONVERSIONS:
        from_unit = units[(measured, from_unit_name)]
        to_unit = units[(measured, to_unit_name)]
        UnitConversion.objects.create(
            from_unit=from_unit,
            to_unit=to_unit,
            factor=factor)


class Migration(migrations.Migration):

    dependencies = [('recipes', '0001_initial')]

    operations = [migrations.RunPython(create_units)]
