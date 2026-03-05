from django.urls import path
from .views import CreatePaymentView, VerifyPaymentView, CreateRefundView

urlpatterns = [
    path('create/<int:order_id>/', CreatePaymentView.as_view(), name='create-payment'),
    path('verify/', VerifyPaymentView.as_view(), name='verify-payment'),
    path("refund/<int:order_id>/", CreateRefundView.as_view()),
    path("refunds/", CreateRefundView.as_view()),
    path("refund/<uuid:refund_id>/", CreateRefundView.as_view()),
]