import uuid
from django.db import models

import random

class GeneralServices:
    def random_generator():
        random_id = str(random.randint(100, 999))
        return random_id

def user_directory_path(instance, filename):
    return f"documents/{filename}"


# create an abstract model with created and updated fields
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Country(BaseModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    phone_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"


class DocumentType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"DOC{GeneralServices.random_generator()}"
        super().save(*args, **kwargs)

class Bank(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{self.name}[:2]{GeneralServices.random_generator()}"
            print(self.code)
        super().save(*args, **kwargs)
