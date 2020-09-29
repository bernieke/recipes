# Generated by Django 2.2.1 on 2019-08-01 19:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0009_allow_tag_and_ingredient_spacing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ingredient',
            options={
                'ordering': ('name',),
                'verbose_name': 'ingredient',
                'verbose_name_plural': 'ingredients'
            },
        ),
        migrations.AlterField(
            model_name='ingredientinrecipe',
            name='ingredient',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='recipes.Ingredient', verbose_name='ingredient'),
        ),
        migrations.CreateModel(
            name='IngredientUnit',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('factor', models.DecimalField(
                    blank=True, decimal_places=3, default=None, max_digits=7,
                    null=True, verbose_name='factor')),
                ('ingredient', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='recipes.Ingredient')),
                ('unit', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='recipes.Unit', verbose_name='unit')),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
                'unique_together': {('ingredient', 'unit')},
            },
        ),
        migrations.AddField(
            model_name='ingredient',
            name='primary_unit',
            field=models.ForeignKey(
                blank=True, default=None, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='primary_unit', to='recipes.Unit',
                verbose_name='primary unit'),
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='ingredient_unit',
            field=models.ForeignKey(
                blank=True, default=None, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='recipes.IngredientUnit', verbose_name='ingredient'),
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredient_units',
            field=models.ManyToManyField(
                blank=True, through='recipes.IngredientInRecipe',
                to='recipes.IngredientUnit', verbose_name='ingredients'),
        ),
    ]