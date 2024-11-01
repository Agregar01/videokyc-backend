import uuid
from django.db import models


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
    currency_code = models.CharField(max_length=20)
    currency_name = models.CharField(max_length=100, null=True, blank=True)
    phone_code = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Countries"


class Currency(BaseModel):
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return {self.code} | {self.name}

    class Meta:
        verbose_name_plural = "Currencies"

class FeeRate(BaseModel):
    rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return str(self.rate)

    class Meta:
        verbose_name_plural = "Fee Rate"

