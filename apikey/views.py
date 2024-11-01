from django.shortcuts import render
from rest_framework import generics, permissions
from authentication.models import Business
from apikey.models import APIKey
from apikey.serializers import APIKeySerializer
from rest_framework.response import Response

from common.services import Statuses

class APIKeyListCreateView(generics.GenericAPIView):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        business_id = self.kwargs.get('business_id')
        api_keys = APIKey.objects.filter(business=business_id)
        if not api_keys.exists():
            return Response({"status": False, "message": "No API keys found for this account."})
        api_keys_data = []
        for api_key in api_keys:
            data = {
                "api_key": api_key.key,
                "api_key_name": api_key.name,
                "api_key_status": api_key.environment,
                "business_id": api_key.business.id,
                "business_name": api_key.business.business_name,  # Changed from business_name to business_name
            }
            api_keys_data.append(data)
        return Response({"status": True, "api_keys": api_keys_data})
    

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        business_id = self.kwargs.get('business_id')
        business = Business.objects.filter(id=business_id).first()
        if business:
            if business.is_approved is True:
                environment = APIKey.APIKeyStatuses.LIVE.value
            else:
                environment = APIKey.APIKeyStatuses.TEST.value
                api_key = APIKey.objects.create(business=business, name=serializer.validated_data["name"], environment=environment)
            return Response({
                "api_key": api_key.key,
                "api_key_name": api_key.name,
                "api_key_status": api_key.environment,
                "business_id": api_key.business.id,
                "business_id": api_key.business.business_name,
                "business_name": api_key.business.user.email
            })
        else:
            return Response({"detail": "Account not found."}, status=404)

