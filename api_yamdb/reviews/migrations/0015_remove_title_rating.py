# Generated by Django 3.2 on 2023-10-20 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0014_auto_20231020_0250'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='title',
            name='rating',
        ),
    ]