from rest_framework import serializers

from .models import APIKeys

class APIKeySerializer(serializers.ModelSerializer):
    # client = serializers.ReadOnlyField
    key = serializers.ReadOnlyField()
    environment = serializers.ReadOnlyField()

    class Meta:
        model = APIKeys
        fields = ['name', 'key', 'created_at', "environment"]
