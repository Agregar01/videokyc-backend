from django.urls import path

from apikeys.views import APIKeyListCreateView


urlpatterns = [
    path('<client_id>/', APIKeyListCreateView.as_view(), name='api_key_list_create'),
]
