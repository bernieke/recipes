# Generated by Django 3.2.5 on 2021-07-07 08:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0024_ingredientunit_use_in_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientunit',
            name='use_in_recipe',
            field=models.BooleanField(default=False),
        ),
    ]