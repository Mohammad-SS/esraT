# Generated by Django 2.2.13 on 2020-07-28 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0016_auto_20200728_1256'),
    ]

    operations = [
        migrations.AddField(
            model_name='setting',
            name='desc1',
            field=models.CharField(default='nothing', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setting',
            name='desc2',
            field=models.CharField(default='nothing', max_length=250),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='setting',
            name='hasTwoVals',
            field=models.BooleanField(default=False),
        ),
    ]
