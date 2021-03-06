# Generated by Django 3.2.5 on 2022-03-19 12:38

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0021_alter_portfolioassets_bought_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfolio',
            name='created_on',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='portfolioassets',
            name='bought_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
