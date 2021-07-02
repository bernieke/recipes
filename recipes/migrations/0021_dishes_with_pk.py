from django.db import migrations


def dishes_with_pk(apps, schema_editor):
    Dishes = apps.get_model('recipes', 'Dishes')

    try:
        dishes = Dishes.objects.get()
        lines = []
        for line in dishes.dishes.split('\n'):
            if line.strip():
                lines.append(f',{line}')
        dishes.dishes = '\n'.join(lines)
        dishes.save()
    except Dishes.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [('recipes', '0020_remove_last_change_id')]

    operations = [migrations.RunPython(dishes_with_pk)]
