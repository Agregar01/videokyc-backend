# Generated by Django 5.1 on 2024-09-19 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('videokyc', '0004_alter_imagecomparison_verification_completed_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='imagecomparison',
            name='othernames',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]