from rest_framework import serializers
from .models import Stock, Supplier

class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ['id', 'category', 'item_name', 'quantity', 're_order', 'last_updated', 'supplier']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'