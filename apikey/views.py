from django.shortcuts import render
from rest_framework import generics, permissions
from authentication.models import Business
from apikey.models import APIKey
from apikey.serializers import APIKeySerializer
from rest_framework.response import Response

class APIKeyListCreateView(generics.GenericAPIView):
    serializer_class = APIKeySerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        account_id = self.kwargs.get('account_id')
        api_keys = APIKey.objects.filter(account=account_id)
        if not api_keys.exists():
            return Response({"status": False, "message": "No API keys found for this account."})
        api_keys_data = []
        for api_key in api_keys:
            data = {
                "api_key": api_key.key,
                "api_key_name": api_key.name,
                "api_key_status": api_key.environment,
                "account_id": api_key.account.id,
                "business_id": api_key.account.business.id,
                "business_name": api_key.account.business.business_name,  # Changed from business_name to business_name
                "user_email": api_key.account.business.user.email  # Corrected the business_name to user_email for email
            }
            api_keys_data.append(data)
        return Response({"status": True, "api_keys": api_keys_data})
    

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        account_id = self.kwargs.get('account_id')
        account = Business.objects.filter(id=account_id).first()
        if account:
            if account.status == Business.AccountStatuses.APPROVED.value:
                environment = APIKey.APIKeyStatuses.LIVE.value
            else:
                environment = APIKey.APIKeyStatuses.TEST.value
                api_key = APIKey.objects.create(account=account, name=serializer.validated_data["name"], environment=environment)
            return Response({
                "api_key": api_key.key,
                "api_key_name": api_key.name,
                "api_key_status": api_key.environment,
                "account_id": api_key.account.id,
                "business_id": api_key.account.business.id,
                "business_id": api_key.account.business.business_name,
                "business_name": api_key.account.business.user.email,

            })
        else:
            return Response({"detail": "Account not found."}, status=404)

