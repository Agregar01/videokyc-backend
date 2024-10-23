from rest_framework import generics
from rest_framework.response import Response

from apikeys.models import APIKeys, Account
from apikeys.serializers import APIKeySerializer

class APIKeyListCreateView(generics.GenericAPIView):
    serializer_class = APIKeySerializer

    def get(self, *args, **kwargs):
        print("jjjjjj")
        client_id = self.kwargs.get('client_id')
        print(client_id)
        try:
            account = Account.objects.get(client_id=client_id)
            print(account)
        except Account.DoesNotExist:
            return APIKeys.objects.none()
        print("gggggggg")
        apikeys = APIKeys.objects.filter(client=account)
        return Response(APIKeySerializer(apikeys, many=True).data)


    def post(self, request, *args, **kwargs):
        print("lllll")
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        client_id = self.kwargs.get('client_id')

        business, _ = Account.objects.get_or_create(client_id=client_id)
        if business:
            api_key = APIKeys.objects.create(client=business, name=serializer.validated_data["name"])
            print(api_key)
            return Response({
                "api_key": api_key.key,
                "api_key_name": api_key.name,
                "api_key_status": api_key.environment,
                "id": api_key.id,
                "client_id": api_key.client.client_id
            })
        
        else:
            return Response({"detail": "Business details not found."}, status=404)

