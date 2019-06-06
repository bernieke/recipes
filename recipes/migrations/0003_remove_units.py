from django.db import migrations


UNITS = [
    ('W', 'tsp'),
    ('W', 'tbsp'),
    ('W', 'cup'),
]


def remove_units(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')

    for measured, name in UNITS:
        try:
            Unit.objects.get(name=name, measured=measured).delete()
        except Unit.DoesNotExist:
            pass


class Migration(migrations.Migration):

    dependencies = [('recipes', '0002_add_units')]

    operations = [migrations.RunPython(remove_units)]
