# Generated by Django 2.2.13 on 2020-06-30 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0008_auto_20200630_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='conductoritem',
            name='photo',
            field=models.ImageField(blank=True, default='default.jpeg', null=True, upload_to='ConductorImages'),
        ),
        migrations.AlterField(
            model_name='archive',
            name='photo',
            field=models.ImageField(blank=True, default='default.jpeg', null=True, upload_to='ArchiveImages'),
        ),
    ]
