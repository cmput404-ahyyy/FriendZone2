# Generated by Django 2.1.7 on 2019-04-05 04:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20190403_0507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='password',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
