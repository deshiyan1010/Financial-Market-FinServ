# Generated by Django 3.2.5 on 2021-12-09 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0013_alter_assetpricemovements_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assetpricemovements',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
