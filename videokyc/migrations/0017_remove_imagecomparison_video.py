# Generated by Django 5.1 on 2024-09-20 13:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videokyc', '0016_alter_imagecomparison_video'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imagecomparison',
            name='video',
        ),
    ]