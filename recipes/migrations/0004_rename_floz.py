from django.db import migrations


def rename_floz(apps, schema_editor):
    Unit = apps.get_model('recipes', 'Unit')

    floz = Unit.objects.get(name='oz', measured='V')
    floz.name = 'fl oz'
    floz.save()


class Migration(migrations.Migration):

    dependencies = [('recipes', '0003_remove_units')]

    operations = [migrations.RunPython(rename_floz)]
