from rest_framework import serializers
from .models import Cart, CartItem
from store.serializers import ProductSerializer
from rest_framework.response import Response
from store.models import Product
class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart 
        fields = "__all__"



class CartItemSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    product = ProductSerializer( read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(source="product", queryset=Product.objects.filter(is_active=True), write_only=True)
    class Meta:
        model = CartItem
        fields = ['cart', 'product', 'quantity', 'product', 'product_id']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError({"error":"Quantity must be a valid integer"})
        return value
        
    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity")
        product_id = data.get("product_id")
        if not product_id:
            return Response({"message": "ID does not exist"})
        if product.stock < quantity:
            return Response({"message":"insufficient stock"})  
            