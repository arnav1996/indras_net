# Generated by Django 2.0.6 on 2018-07-25 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('IndrasNet', '0003_auto_20180614_1812'),
    ]

    operations = [
        migrations.AddField(
            model_name='model',
            name='functional',
            field=models.BooleanField(default=False),
        ),
    ]
