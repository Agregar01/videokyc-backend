# Generated by Django 5.1 on 2024-11-01 05:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='teammember',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
