# Generated by Django 5.1.5 on 2025-03-05 11:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_rename_comment_count_product_comments_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='commentproduct',
            old_name='is_public',
            new_name='is_published',
        ),
    ]
