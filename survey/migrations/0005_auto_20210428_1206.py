# Generated by Django 3.1.4 on 2021-04-28 12:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_question_blank'),
    ]

    operations = [
        migrations.RenameField(
            model_name='survey',
            old_name='modify',
            new_name='modifiable',
        ),
    ]
