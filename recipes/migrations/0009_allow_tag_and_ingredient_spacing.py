# Generated by Django 2.2.1 on 2019-06-08 07:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0008_add_markdown'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag',
            name='break_after',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='category',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to='recipes.Category', verbose_name='category'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='name',
            field=models.CharField(
                blank=True, max_length=254, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='ingredient',
            name='unit',
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.PROTECT,
                to='recipes.Unit', verbose_name='unit'),
            preserve_default=False,
        ),
    ]