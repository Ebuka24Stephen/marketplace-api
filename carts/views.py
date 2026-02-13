from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import F
from .models import Cart, CartItem
from store.models import Product



class CartListApiView(APIView):
    permission_classes = []
    def get(self, request, product_id, cart_id=None):
        product = get_object_or_404(Product, id=product_id)
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({"items": []})
        cart = Cart.objects.filter(id=cart_id).first()
        if not cart:
            return Response({"items": []})
        items = CartItem.objects.filter(cart=cart).select_related("product")
        return Response({
            "cart_id": cart.id,
            "items": [
                {
                    "id": i.id,
                    "product": i.product.slug,
                    "name": i.product.name,
                    "price": str(i.product.price),
                    "quantity": i.quantity,
                    "stock": i.product.stock,
                }
                for i in items
            ]
        })
    

class CartItemQuantityView(APIView):
    permission_classes = []
    def patch(self, request, item_id):
        cart_id = request.session.get("cart_id")
        if not cart_id:
            return Response({
                "error": f"Cart with that id does not exist!"
            })
        quantity = int(request.data.get("quantity", 1))
        if quantity <1:
            return Response({
                "message": "quantity must be 1 or above"
            })
        item = CartItem.objects.select_related("product").filter(id=item_id, cart_id=cart_id).first()
        if not item:
            return Response({"error": "Item not found"}, status=404)
        if quantity > item.product.stock:
            return Response({
                "message": "Product is out of stock!"
            })
        item.quantity == quantity
        item.save(update_fields=['quantity'])
        return Response({"id": item.id, "quantity": item.quantity})


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
