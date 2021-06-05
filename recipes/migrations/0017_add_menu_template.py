from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0016_recipe_popularity'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True,
                                        serialize=False, verbose_name='ID')),
                ('name', models.TextField(verbose_name='name')),
                ('active', models.BooleanField(
                    default=False, verbose_name='active')),
                ('monday_lunch_note', models.TextField(
                    blank=True, verbose_name='Monday lunch')),
                ('monday_dinner_note', models.TextField(
                    blank=True, verbose_name='Monday dinner')),
                ('tuesday_lunch_note', models.TextField(
                    blank=True, verbose_name='Tuesday lunch')),
                ('tuesday_dinner_note', models.TextField(
                    blank=True, verbose_name='Tuesday dinner')),
                ('wednesday_lunch_note', models.TextField(
                    blank=True, verbose_name='Wednesday lunch')),
                ('wednesday_dinner_note', models.TextField(
                    blank=True, verbose_name='Wednesday dinner')),
                ('thursday_lunch_note', models.TextField(
                    blank=True, verbose_name='Thursday lunch')),
                ('thursday_dinner_note', models.TextField(
                    blank=True, verbose_name='Thursday dinner')),
                ('friday_lunch_note', models.TextField(
                    blank=True, verbose_name='Friday lunch')),
                ('friday_dinner_note', models.TextField(
                    blank=True, verbose_name='Friday dinner')),
                ('saturday_lunch_note', models.TextField(
                    blank=True, verbose_name='Saturday lunch')),
                ('saturday_dinner_note', models.TextField(
                    blank=True, verbose_name='Saturday dinner')),
                ('sunday_lunch_note', models.TextField(
                    blank=True, verbose_name='Sunday lunch')),
                ('sunday_dinner_note', models.TextField(
                    blank=True, verbose_name='Sunday dinner')),
            ],
        ),
    ]
