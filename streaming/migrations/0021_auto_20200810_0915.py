# Generated by Django 2.2.13 on 2020-08-10 09:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0020_auto_20200809_1127'),
    ]

    operations = [
        migrations.AlterField(
            model_name='archive',
            name='addTime',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
