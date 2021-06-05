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
                ('name', models.CharField(max_length=64, unique=True, verbose_name='name')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, verbose_name='order')),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='name')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.Category', verbose_name='category')),
            ],
            options={
                'verbose_name': 'ingredient',
                'verbose_name_plural': 'ingredients',
                'ordering': ['name', 'unit'],
            },
        ),
        migrations.CreateModel(
            name='IngredientInRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=7, verbose_name='amount')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=0, verbose_name='order')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='recipes.Ingredient', verbose_name='ingredient')),
            ],
            options={
                'verbose_name': 'ingredient',
                'verbose_name_plural': 'ingredients',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, unique=True, verbose_name='name')),
                ('order', models.PositiveSmallIntegerField(db_index=True, default=32767, verbose_name='order')),
            ],
            options={
                'verbose_name': 'tag',
                'verbose_name_plural': 'tags',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=16, verbose_name='name')),
                ('measured', models.CharField(choices=[('P', 'piece'), ('W', 'weight'), ('V', 'volume'), ('L', 'length')], max_length=1, verbose_name='measured')),
            ],
            options={
                'verbose_name': 'unit',
                'verbose_name_plural': 'units',
                'ordering': ['name', 'measured'],
                'unique_together': {('name', 'measured')},
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=254, unique=True, verbose_name='title')),
                ('recipe', models.TextField(blank=True, verbose_name='recipe')),
                ('ingredients', models.ManyToManyField(blank=True, through='recipes.IngredientInRecipe', to='recipes.Ingredient', verbose_name='ingredients')),
                ('tags', models.ManyToManyField(blank=True, to='recipes.Tag', verbose_name='tags')),
            ],
            options={
                'verbose_name': 'recipe',
                'verbose_name_plural': 'recipes',
                'ordering': ['title'],
            },
        ),
        migrations.AddField(
            model_name='ingredientinrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Recipe', verbose_name='recipe'),
        ),
        migrations.AddField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='recipes.Unit', verbose_name='unit'),
        ),
        migrations.CreateModel(
            name='Alias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, unique=True, verbose_name='name')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recipes.Ingredient', verbose_name='ingredient')),
            ],
            options={
                'verbose_name': 'alias',
                'verbose_name_plural': 'aliases',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UnitConversion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('factor', models.DecimalField(decimal_places=3, max_digits=7, verbose_name='factor')),
                ('from_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='from_unit', to='recipes.Unit', verbose_name='from unit')),
                ('to_unit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='to_unit', to='recipes.Unit', verbose_name='to unit')),
            ],
            options={
                'verbose_name': 'unit conversion',
                'verbose_name_plural': 'unit conversions',
                'ordering': ['from_unit', 'to_unit'],
                'unique_together': {('from_unit', 'to_unit')},
            },
        ),
        migrations.AlterUniqueTogether(
            name='ingredient',
            unique_together={('name', 'unit')},
        ),
    ]
