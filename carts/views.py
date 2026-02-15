from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Cart, CartItem
from store.models import Product
from django.db import transaction

class AddtoCartApiView(APIView):
    @transaction.atomic
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id, is_active=True)

        cart_id = request.session.get("cart_id")
        cart = Cart.objects.filter(id=cart_id).first() if cart_id else None

        if not cart:
            cart = Cart.objects.create()
            request.session["cart_id"] = cart.id

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": 1},
        )

        if not created:
            updated = CartItem.objects.filter(
                id=item.id,
                quantity__lt=F("product__stock"),
            ).update(quantity=F("quantity") + 1)

            if updated == 0:
                return Response({"message": "Product is out of stock!"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "Added to cart"}, status=status.HTTP_200_OK)


class CartListApiView(APIView):
    permission_classes = []
    def get(self, request):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        cart = Cart.objects.prefetch_related("items__product").filter(id=cart_id).first()
        if not cart or not cart.items.exists():
            return Response({"message": "Cart is empty"}, status=status.HTTP_200_OK)
        items_data = []
        for item in cart.items.all():
            items_data.append({
                "id": item.id,
                "product": {
                    "id": item.product.id,
                    "name": item.product.name,
                    "price": str(item.product.price),
                },
                "quantity": item.quantity,
                "subtotal": str(item.subtotal),
            })

        return Response({
            "cart_id": cart.id,
            "total_price": str(cart.total_price),
            "items": items_data
        }, status=status.HTTP_200_OK)

    

class CartItemQuantityView(APIView):
    permission_classes = []
    def patch(self, request, item_id):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({
                "error": f"Cart with that id does not exist!"
            })
        cart = get_object_or_404(Cart, id=cart_id)
        item = get_object_or_404(CartItem, id=item_id, cart=cart)
        if item.quantity >= item.product.stock:
            return Response({"error": "Cannot increase quantity. Product is out of stock."}, status=status.HTTP_400_BAD_REQUEST)
        item.quantity += 1
        item.save(update_fields=["quantity", "added_at"])
        return Response({"message": "Quantity updated", "quantity": item.quantity}, status=status.HTTP_200_OK)


class CartItemDelete(APIView):
    permission_classes = []
    def delete(self, request, item_id):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"error": "No active cart"}, status=status.HTTP_400_BAD_REQUEST)
        item = CartItem.objects.filter(id=item_id, cart_id=cart_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response({"deleted": True, "id": item_id}, status=status.HTTP_200_OK)
