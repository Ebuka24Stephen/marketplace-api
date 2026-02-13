from django.urls import path
from .views import CartListApiView, CartItemQuantityView, CartItemDelete

urlpatterns = [
    path("products/<int:product_id>/", CartListApiView.as_view(), name="cart-list"),
    path("items/<int:item_id>/quantity/", CartItemQuantityView.as_view(), name="cart-item-quantity"),
    path("items/<int:item_id>/delete/", CartItemDelete.as_view(), name="cart-item-delete"),
]
