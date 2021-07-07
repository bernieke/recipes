# Generated by Django 2.2.24 on 2021-07-01 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0019_weekmenu_per_week'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('order', 'name'),
                     'verbose_name': 'category',
                     'verbose_name_plural': 'categories'},
        ),
        migrations.RemoveField(
            model_name='dishes',
            name='last_change_id',
        ),
        migrations.RemoveField(
            model_name='menu',
            name='last_change_id',
        ),
    ]