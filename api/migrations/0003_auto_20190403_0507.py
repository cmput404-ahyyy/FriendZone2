# Generated by Django 2.1.7 on 2019-04-03 05:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20190403_0045'),
    ]

    operations = [
        migrations.RenameField(
            model_name='author',
            old_name='userName',
            new_name='username',
        ),
    ]
