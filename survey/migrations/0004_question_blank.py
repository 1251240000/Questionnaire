# Generated by Django 3.1.4 on 2021-04-28 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0003_auto_20210427_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='blank',
            field=models.BooleanField(default=True, verbose_name='是否允许为空'),
        ),
    ]
