# Generated by Django 5.1 on 2024-09-19 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videokyc', '0005_imagecomparison_othernames'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagecomparison',
            name='verification_duration',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]