from django.urls import path
from .views import CartListApiView, AddtoCartApiView

urlpatterns = [
    path("", CartListApiView.as_view(), name="cart-list"),
   
    path("add/", AddtoCartApiView.as_view(), name="add-to-cart"),
]