# Generated by Django 3.2.18 on 2023-05-05 22:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20230504_1958'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='todo',
            name='completed',
        ),
        migrations.RemoveField(
            model_name='todo',
            name='description',
        ),
    ]
