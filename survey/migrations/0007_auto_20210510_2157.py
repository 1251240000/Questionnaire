# Generated by Django 3.1.4 on 2021-05-10 13:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0006_auto_20210502_0635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='order',
            field=models.IntegerField(default=1, verbose_name='题目序号'),
        ),
    ]
