from django.db import migrations


def menu_dishes_with_pk(apps, schema_editor):
    Menu = apps.get_model('recipes', 'Menu')

    for menu in Menu.objects.all():
        for day in ['monday', 'tuesday', 'wednesday', 'thursday',
                    'friday', 'saturday', 'sunday']:
            for meal in ['lunch', 'dinner']:
                dishes = getattr(menu, f'{day}_{meal}_dishes')
                lines = []
                for line in dishes.split('\n'):
                    if line.strip():
                        lines.append(f',{line}')
                setattr(menu, f'{day}_{meal}_dishes', '\n'.join(lines))
        menu.save()


class Migration(migrations.Migration):

    dependencies = [('recipes', '0021_dishes_with_pk')]

    operations = [migrations.RunPython(menu_dishes_with_pk)]
