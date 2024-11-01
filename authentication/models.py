import enum
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from authentication.managers import CustomUserManager
from authentication.services import GeneralServices
from common.models import BaseModel
from django.db import transaction

general_services = GeneralServices

def business_directory_path(instance, filename):
    name = instance.business_name.replace(" ", "_")
    return f"documents/{name}/{filename}"

class User(AbstractBaseUser, BaseModel):

    BusinessTypes = [
        ('Sole Proprietor', 'Sole Proprietor'),
        ('Partnership', 'Partnership'),
        ('Limited Liability', 'Limited Liability'),
    ]
    business_type = models.CharField(max_length=30, choices=BusinessTypes)
    business_name = models.CharField(
        _("Business Name"), max_length=200, blank=True, null=True
    )
    firstname = models.CharField(_("First Name"), max_length=100, blank=True, null=True)
    lastname = models.CharField(_("Last Name"), max_length=100, blank=True, null=True)

    email = models.EmailField(
        _("Email"), unique=True, max_length=200, null=False, blank=False
    )
    phone = models.CharField(
        _("Phone"), max_length=30, unique=True, null=True, blank=True
    )
    is_email_verified = models.BooleanField(_("Email Verified"), default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    password = models.CharField(max_length=200)
    is_primary_account=models.BooleanField(null=True, blank=True)

    objects = CustomUserManager()
    user_name = None
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.id} | {self.firstname} | {self.lastname} | {self.email}"

    @property
    def get_email(self):
        return self.email

    @property
    def get_fullname(self):
        return f"{self.firstname} {self.lastname}"

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    def save(self, *args, **kwargs):
        if self.firstname:
            self.firstname = self.firstname.capitalize()
        if self.lastname:
            self.lastname = self.lastname.capitalize()
        if self.business_name:
            self.is_primary_account = True
        self.email = self.email.lower()
        super().save(*args, **kwargs)


class Business(BaseModel):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    business_type = models.CharField(max_length=100)
    business_name = models.CharField(
        _("Business Name"), max_length=200, blank=True, null=True
    )
    is_kyc_submitted = models.BooleanField(_("KYC Submitted"), default=False)
    address = models.CharField(_("Business Address"), max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(_("Business Approved"), default = False, null=True, blank=True)
    business_docs_submitted = models.BooleanField(_("Business Docs Submitted"), default=False)
    public_business_id = models.CharField(_("Public User ID"), max_length=30, blank=True, null=True)
    registration_documents = models.FileField(
        _("Business Documents"), upload_to=business_directory_path, max_length=255
    )
    id_image_director_1 = models.FileField(
        _("ID image of Director 1"), upload_to=business_directory_path, max_length=255
    )
    id_image_director_2 = models.FileField(
        _("ID image of Director 2"), upload_to=business_directory_path, max_length=255
    )
    logo = models.FileField(_("Logo"), upload_to=business_directory_path, max_length=255)
    tax_identification = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.business_name} --- {self.user.email} --- {self.user.get_fullname} "
    
    @property
    def get_business_name(self):
        return self.business_name

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self.business_name:
            self.business_name = self.business_name.capitalize()
        self.public_business_id = f"KPB{general_services.random_generator()}"
        super().save(*args, **kwargs)


class OTP(BaseModel):
    otp = models.CharField(max_length=8, blank=True, null=True)
    email = models.CharField(max_length=200, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} {self.otp}"
