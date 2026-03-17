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
        if not product_id:
            return Response({"message": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.select_for_update().get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            quantity = int(request.data.get("quantity", 1))
        except (ValueError, TypeError):
            return Response({"error": "Quantity must be a number"}, status=status.HTTP_400_BAD_REQUEST)
 
        if quantity < 1:
            return Response({"error": "Invalid quantity"}, status=status.HTTP_400_BAD_REQUEST)
        
        cart_id = request.session.get("cart_id")
        
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None
        if not cart:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id

        existing_qty = (CartItem.objects.filter(cart=cart, product=product).values_list("quantity", flat=True).first() or 0)
        if product.stock < (quantity + existing_qty):
            return Response({"error": "Insufficient stock"}, status=status.HTTP_400_BAD_REQUEST)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity":quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()

        

        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)

class ReduceCartQuantityView(APIView):
    permission_classes = [AllowAny]
    @transaction.atomic
    def post(self, request, product_id):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        product = get_object_or_404(Product, id=product_id)


        cart = get_object_or_404(Cart, id=cart_id)
        item = get_object_or_404(CartItem.objects.select_for_update(), cart=cart, product=product)

        item.quantity -= 1
        
        if item.quantity <= 0:
            item.delete()
            return Response({"message": "Item removed from cart"}, status=status.HTTP_200_OK)
        item.save()
        
        return Response({
            "message": "Quantity reduced",
            "quantity": item.quantity
        }, status=status.HTTP_200_OK)


class CartListApiView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle]
    def get(self, request):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        cart = Cart.objects.filter(id=cart_id).first()
        if not cart:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        items =  CartItem.objects.filter(cart=cart).select_related("product")

        if not items.exists():
            return Response({"message": "Empty Cart"}, status=status.HTTP_200_OK)
        cart_total = sum(item.subtotal for item in items)
        data = [
            {
                "product_id": item.product.id,
                "product": item.product.name,
                "price": item.product.price,
                "quantity": item.quantity,
                "total": item.subtotal,
                
            } for item in items]
        return Response({
            "items": data,
            "cart_total": cart_total
        }, status=status.HTTP_200_OK)



class CartDeleteProduct(APIView):
    permission_classes = [AllowAny]

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({
                "message": "empty cart"
            }, status=status.HTTP_404_NOT_FOUND)
        cart = get_object_or_404(Cart, id=cart_id)
        item = get_object_or_404(CartItem, cart=cart, product=product)
        
        item.delete()
        
        return Response({
            "message": "Product removed from cart",
        }, status=status.HTTP_200_OK)