from rest_framework import viewsets
from .models import Stock, Supplier
from .serializers import StockSerializer, SupplierSerializer

class StockViewSet(viewsets.ModelViewSet):
    queryset = Stock.objects.all()
    serializer_class = StockSerializer
    search_fields = ['item_name', 'category__group']

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer