import re

from django.db import migrations


RE_QTY = r'(\d*,.*) \((\d+\.?\d*)\)'


def extract_qty(line):
    try:
        return ','.join(re.match(RE_QTY, line).groups())
    except AttributeError:
        return f'{line},1'


def menu_dishes_with_qty(apps, schema_editor):
    Dishes = apps.get_model('recipes', 'Dishes')
    Menu = apps.get_model('recipes', 'Menu')

    try:
        dishes = Dishes.objects.get()
        lines = []
        for line in dishes.dishes.split('\n'):
            if line.strip():
                lines.append(extract_qty(line))
        dishes.dishes = '\n'.join(lines)
        dishes.save()
    except Dishes.DoesNotExist:
        pass

    for menu in Menu.objects.all():
        for day in ['monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday']:
            for meal in ['lunch', 'dinner']:
                dishes = getattr(menu, f'{day}_{meal}_dishes')
                lines = []
                for line in dishes.split('\n'):
                    if line.strip():
                        lines.append(extract_qty(line))
                setattr(menu, f'{day}_{meal}_dishes', '\n'.join(lines))
        menu.save()


class Migration(migrations.Migration):

    dependencies = [('recipes', '0026_rename_primary_unit')]

    operations = [migrations.RunPython(menu_dishes_with_qty)]
