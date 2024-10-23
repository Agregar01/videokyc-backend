from rest_framework import serializers
from common.models import Country, DocumentType


class DocumentTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    code = serializers.ReadOnlyField()
    class Meta:
        model = DocumentType
        fields = ['id', 'name', 'code']
        
class CountrySerializer(serializers.ModelSerializer):
    name = serializers.CharField(max_length=100, required=True)
    code = serializers.ReadOnlyField()
    class Meta:
        model = Country
        fields = ['id', 'name', 'code']
