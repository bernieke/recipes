from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0)),
            ],
            options={
                'ordering': ('order', 'name'),
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('packaged', models.PositiveSmallIntegerField(default=None, null=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.Category')),
            ],
            options={
                'ordering': ('name', 'unit'),
            },
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=7)),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.Ingredient')),
            ],
            options={
                'verbose_name': 'Ingredient',
                'ordering': ('order',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16)),
                ('measured', models.CharField(choices=[('W', 'weight'), ('V', 'volume')], max_length=1)),
            ],
            options={
                'ordering': ('name', 'measured'),
                'unique_together': {('name', 'measured')},
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=254, unique=True)),
                ('recipe', models.TextField(blank=True)),
                ('ingredients', models.ManyToManyField(blank=True, through='recipes.IngredientInRecipe', to='recipes.Ingredient')),
                ('tags', models.ManyToManyField(blank=True, to='recipes.Tag')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='recipes.Unit'),
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, unique=True)),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='UnitConversion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.DecimalField(decimal_places=3, max_digits=7)),
                ('unit_from', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_from', to='recipes.Unit')),
                ('unit_to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_to', to='recipes.Unit')),
            ],
            options={
                'ordering': ('unit_from', 'unit_to'),
                'unique_together': {('unit_from', 'unit_to')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'unit')},
        ),
    ]
