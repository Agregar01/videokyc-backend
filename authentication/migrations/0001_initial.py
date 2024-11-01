# Generated by Django 5.1 on 2024-10-30 17:03

import authentication.models
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OTP',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('otp', models.CharField(blank=True, max_length=8, null=True)),
                ('email', models.CharField(blank=True, max_length=200, null=True)),
                ('is_verified', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_type', models.CharField(choices=[('Sole Proprietor', 'Sole Proprietor'), ('Partnership', 'Partnership'), ('Limited Liability', 'Limited Liability')], max_length=30)),
                ('business_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Business Name')),
                ('firstname', models.CharField(blank=True, max_length=100, null=True, verbose_name='First Name')),
                ('lastname', models.CharField(blank=True, max_length=100, null=True, verbose_name='Last Name')),
                ('email', models.EmailField(max_length=200, unique=True, verbose_name='Email')),
                ('phone', models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='Phone')),
                ('is_email_verified', models.BooleanField(default=False, verbose_name='Email Verified')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('password', models.CharField(max_length=200)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='Business',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('business_type', models.CharField(max_length=100)),
                ('business_name', models.CharField(blank=True, max_length=200, null=True, verbose_name='Business Name')),
                ('is_kyc_submitted', models.BooleanField(default=False, verbose_name='KYC Submitted')),
                ('address', models.CharField(blank=True, max_length=100, null=True, verbose_name='Business Address')),
                ('is_approved', models.BooleanField(blank=True, default=False, null=True, verbose_name='Business Approved')),
                ('business_docs_submitted', models.BooleanField(default=False, verbose_name='Business Docs Submitted')),
                ('public_business_id', models.CharField(blank=True, max_length=30, null=True, verbose_name='Public User ID')),
                ('registration_documents', models.FileField(max_length=255, upload_to=authentication.models.business_directory_path, verbose_name='Business Documents')),
                ('id_image_director_1', models.FileField(max_length=255, upload_to=authentication.models.business_directory_path, verbose_name='ID image of Director 1')),
                ('id_image_director_2', models.FileField(max_length=255, upload_to=authentication.models.business_directory_path, verbose_name='ID image of Director 2')),
                ('logo', models.FileField(max_length=255, upload_to=authentication.models.business_directory_path, verbose_name='Logo')),
                ('tax_identification', models.CharField(blank=True, max_length=50, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='authentication.user')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
