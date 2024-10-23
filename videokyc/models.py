import random
from django.db import models
from common.models import BaseModel
from django.core.exceptions import ValidationError

def bank_client_directory(instance, filename):
    return f"{filename}"

class VERIFICATION_STATUS_CHOICES(models.TextChoices):
    MATCH_FOUND = "MATCH",
    MATCH_NOT_FOUND = "MISMATCH",
    PENDING = "PENDING"

class EMAIL_STATUS_CHOICES(models.TextChoices):
    DELIVERED = "DELIVERED",
    NOT_DELIVERED = "NOT DELIVERED",
    PENDING = "PENDING"

class VerificationTypes(models.TextChoices):
    ONBOARDING = "ONBOARDING", "Onboarding"
    STANDARD_VERIFICATION = "STANDARD", "Standard"


def random_generator():
    random_id = str(random.randint(100000000000000, 999999999999999))
    return random_id

class ImageComparison(BaseModel):
    external_id = models.CharField(max_length=30, blank=True, null=True)
    phone = models.CharField(max_length=13)
    email = models.EmailField(max_length=255)
    submitted_image = models.FileField(upload_to=bank_client_directory, null=True, blank=True)
    video_image = models.FileField(upload_to=bank_client_directory, null=True, blank=True)
    verification_status = models.CharField(max_length=20, default=VERIFICATION_STATUS_CHOICES.PENDING.value)
    email_status = models.CharField(max_length=20, default=EMAIL_STATUS_CHOICES.PENDING.value)
    api_key = models.CharField(max_length=50, null=False, blank=False)
    callback_url = models.URLField(max_length=200, blank=True, null=True)
    initiator = models.JSONField(blank=True, null=True, default=dict)
    longitude = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=20, null=True, blank=True)
    firstname = models.CharField(max_length=200, null=True, blank=True)
    lastname = models.CharField(max_length=200, null=True, blank=True)
    othernames = models.CharField(max_length=200, null=True, blank=True)
    fullname = models.CharField(max_length=200, null=True, blank=True)
    link_sent_time = models.DateTimeField(auto_now=True)
    video_verification_start_time = models.CharField(null=True, blank=True)
    verification_completed_time = models.DateTimeField(auto_now=True, null=True, blank=True)
    verification_duration = models.DateTimeField(auto_now=True, null=True, blank=True)
    verification_completed = models.BooleanField(default=True)
    date_of_birth = models.CharField(max_length=40, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    verification_reason = models.CharField(null=True, blank=True)
    client_id = models.CharField(null=False, blank=False)
    device_info = models.JSONField(null=True, blank=True)
    liveliness_detection = models.JSONField(null=True, blank=True)
    consent_sorted = models.BooleanField(null=False, blank=False, default=False)
    sim_swap_details = models.JSONField(null=True, blank=True)
    type = models.CharField(max_length=50, choices=VerificationTypes.choices, null=False, blank=False)
    description = models.TextField(null=True)
    ofac_verification = models.JSONField(null=True, blank=True)
    video_verification_details = models.JSONField(null=True, blank=True)
    # video = models.FileField(upload_to=bank_client_directory, null=True, blank=True)


    def __str__(self):
        return f"{self.id} || {self.phone} || {self.email}"
    
    def save(self, *args, **kwargs):
        max_length = 100
        if not self.reference:
            self.reference = f"AV{random_generator()}"
        if self.submitted_image and len(self.submitted_image.name) > max_length:
            raise ValueError(f"The image name is too long. Maximum length is {max_length} characters.")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ("-created_at", )


class Link(BaseModel):
    email = models.EmailField(max_length=255)
    link = models.CharField(max_length=200)

    def __str__(self):
        return self.email
    
class DocvecLink(BaseModel):
    email = models.EmailField(max_length=255)
    link = models.CharField(max_length=200)

    def __str__(self):
        return self.email