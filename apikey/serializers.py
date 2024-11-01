from rest_framework import serializers

from .models import APIKey

class APIKeySerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()
    key = serializers.ReadOnlyField()
    environment = serializers.ReadOnlyField()

    class Meta:
        model = APIKey
        fields = ['name', 'account', 'key', 'created_at', "environment"]

    # def get_account(self, obj):
    #     return obj