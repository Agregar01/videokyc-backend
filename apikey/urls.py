from django.urls import path
from apikey.views import APIKeyListCreateView


urlpatterns = [
    path('apikeys/<uuid:business_id>/', APIKeyListCreateView.as_view(), name='api_key_list_create'),
]
