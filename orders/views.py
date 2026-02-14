from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, OrderItem 
from store.models import Product
from .serializers import OrderItemSerializer, OrderSerializer
from carts.models import Cart, CartItem
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import F
from rest_framework.exceptions import ValidationError

class OrderCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            raise ValidationError({"error": "No active cart"})
        cart = get_object_or_404(Cart, id=cart_id)
        cart_items = (
            CartItem.objects.select_related("product").select_for_update().filter(cart=cart)
        )
        if not cart_items.exists():
            raise ValidationError({"error": "Cart is empty"})
        serializer = OrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        for item in cart_items:
            updated = Product.objects.filter(
                id=item.product_id,
                stock__gte=item.quantity
            ).update(stock=F("stock") - item.quantity)
            if updated == 0:
                raise ValidationError({"error": f"Not enough stock for {item.product.name}"})
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,   
                quantity=item.quantity
            )
        cart_items.delete()
        cart.delete()
        request.session.pop("cart_id", None)

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Order.objects.filter(user=request.user).prefetch_related("items__product").order_by("-created")
        )
        return Response(OrderSerializer(qs, many=True).data)
    
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        order = get_object_or_404(
            Order.objects.prefetch_related("items__product"),
            pk=pk,
            user=request.user
        )
        return Response(OrderSerializer(order).data)