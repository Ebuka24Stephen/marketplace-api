from django.urls import path
from .views import OrderCreateView, OrderListView, OrderDetailView

urlpatterns = [
    path("checkout/", OrderCreateView.as_view(), name="order-create"),
    path("", OrderListView.as_view(), name="order-list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    
]
