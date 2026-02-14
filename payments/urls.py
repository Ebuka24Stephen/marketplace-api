from django.urls import path
from .views import CreatePaymentView, VerifyPaymentView

urlpatterns = [
    path('create/<int:order_id>/', CreatePaymentView.as_view(), name='create-payment'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
]