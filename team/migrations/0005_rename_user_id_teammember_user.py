# Generated by Django 5.1 on 2024-11-01 12:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0004_teammember_user_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teammember',
            old_name='user_id',
            new_name='user',
        ),
    ]
