# Generated by Django 5.1 on 2024-09-19 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videokyc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagecomparison',
            name='initiator',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]