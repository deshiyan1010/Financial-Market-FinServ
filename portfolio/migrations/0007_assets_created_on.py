# Generated by Django 3.2.5 on 2021-12-09 10:15

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0006_rename_assetname_assets_asset'),
    ]

    operations = [
        migrations.AddField(
            model_name='assets',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]