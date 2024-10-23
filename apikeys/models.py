from common.models import BaseModel
import enum
from django.db import models
import secrets

class Account(BaseModel):
    client_id = models.CharField(max_length=50, unique=True)


class APIKeys(BaseModel):

    class APIKeyStatuses(enum.Enum):
        LIVE = "LIVE"
        TEST = "TEST"

    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=100, unique=True)
    environment = models.CharField(max_length=10, default=APIKeyStatuses.TEST.value)
    created_at = models.DateTimeField(auto_now_add=True)
    client = models.ForeignKey(Account, related_name='api_key', on_delete=models.CASCADE)


    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(32) 
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key