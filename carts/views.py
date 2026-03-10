from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Cart, CartItem
from store.models import Product
from django.db import transaction
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle

class AddtoCartApiView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    @transaction.atomic
    def post(self, request):
        product_id = request.data.get("product_id")
        product = get_object_or_404(Product, id=product_id,is_active=True)
        quantity = request.data.get("quantity")
        cart_id = request.session.get("cart_id")
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None
        if not cart:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            quantity=quantity
        )
        item.product.stock -=1
        item.product.save()
        item.save()
    
        if not created:
            item.quantity +=1 
            item.save()
        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)




class CartListApiView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    def get(self, request):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        cart = Cart.objects.filter(id=cart_id).first()
        if not cart:
            return Response({"message": "Cart not found"})
        items = CartItem.objects.filter(cart=cart)
        if not items.exists():
            return Response({"message": "Empty Cart"})
        data = [
            {
                "product": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "total": item.subtotal,
                
            } for item in items]
        return Response(data, status=status.HTTP_200_OK)

