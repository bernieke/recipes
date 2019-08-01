from django.db import migrations


def rename_floz(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')

    try:
        floz = Unit.objects.get(name='oz', measured='V')
        floz.name = 'fl oz'
        floz.save()
    except Unit.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [('recipes', '0003_remove_units')]

    operations = [migrations.RunPython(rename_floz)]
