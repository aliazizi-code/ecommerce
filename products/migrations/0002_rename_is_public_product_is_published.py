# Generated by Django 5.1.5 on 2025-02-17 13:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='is_public',
            new_name='is_published',
        ),
    ]
