from django.urls import path

from common.views import CountryView, DocumentTypeView


urlpatterns = [
    path("document-type/", DocumentTypeView.as_view(), name = "document-type"),
    path("countries/", CountryView.as_view(), name = "countries"),
]
