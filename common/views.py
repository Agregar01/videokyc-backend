from rest_framework.generics import ListCreateAPIView

from common.models import Country, DocumentType
from common.serializers import CountrySerializer, DocumentTypeSerializer


# Create your views here.
class DocumentTypeView(ListCreateAPIView):
    serializer_class = DocumentTypeSerializer
    queryset = DocumentType.objects.all()
    
class CountryView(ListCreateAPIView):
    serializer_class = CountrySerializer
    queryset = Country.objects.all()