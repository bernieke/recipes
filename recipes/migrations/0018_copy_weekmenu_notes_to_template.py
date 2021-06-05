from django.db import migrations


def move_notes_to_template(apps, schema_editor):
    Menu = apps.get_model('recipes', 'Menu')
    MenuTemplate = apps.get_model('recipes', 'MenuTemplate')

    try:
        menu = Menu.objects.get()
        MenuTemplate.objects.create(
            name='migrated from weekmenu',
            active=True,
            monday_lunch_note=menu.monday_lunch_note,
            tuesday_lunch_note=menu.tuesday_lunch_note,
            wednesday_lunch_note=menu.wednesday_lunch_note,
            thursday_lunch_note=menu.thursday_lunch_note,
            friday_lunch_note=menu.friday_lunch_note,
            saturday_lunch_note=menu.saturday_lunch_note,
            sunday_lunch_note=menu.sunday_lunch_note,
            monday_dinner_note=menu.monday_dinner_note,
            tuesday_dinner_note=menu.tuesday_dinner_note,
            wednesday_dinner_note=menu.wednesday_dinner_note,
            thursday_dinner_note=menu.thursday_dinner_note,
            friday_dinner_note=menu.friday_dinner_note,
            saturday_dinner_note=menu.saturday_dinner_note,
            sunday_dinner_note=menu.sunday_dinner_note)
    except Menu.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [('recipes', '0017_add_menu_template')]

    operations = [migrations.RunPython(move_notes_to_template)]
