import requests
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from orders.models import Order, OrderItem
from .models import Payment
import uuid
from django.conf import settings

PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/{}"
paystack_url = "https://api.paystack.co/transaction/initialize"

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.is_paid:
            return Response({"detail": "Order is already paid."}, status=status.HTTP_400_BAD_REQUEST)
        amount_kobo = int(order.get_sum_total() * 100)  # Convert to kobo
        #create payment record
        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "user": request.user,
                "amount": amount_kobo,
                "currency": payment.currency,
                "reference": f"ORD_{order.id}_{uuid.uuid4().hex[:10]}",
            }

        )
        if not created and  payment.status != payment.Status.PENDING:
            return Response({"detail": "Payment already initialized."}, status=status.HTTP_400_BAD_REQUEST)
        payload = {
            "email": request.user.email,
            "amount": amount_kobo,
            "reference": payment.reference,
            "currency": payment.currency,
            "metadata": {
                "order_id": order.id,
                "user_id": request.user.id,
            },
            }            
        headers= {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.post(self.paystack_url, json=payload, headers=headers)
        if response.status_code != 200:
            return Response({"detail": "Failed to initialize payment."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        if not data.get("status"):
            return Response({"detail": "Payment initialization failed."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        payment.access_code = data["data"]["access_code"]
        payment.save(update_fields=["access_code", "updated"])
        return Response(
            {
                "reference": payment.reference,
                "access_code": payment.access_code,
                "authorization_url": data["data"]["authorization_url"],
            },
            status=200,
        )
    
class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        reference = request.query_params.get("reference")
        if not reference:
            return Response({"detail": "Reference is required."}, status=status.HTTP_400_BAD_REQUEST)
        payment = get_object_or_404(Payment, reference=reference, user=request.user)
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        }
        response = requests.get(PAYSTACK_VERIFY_URL.format(reference=reference), headers=headers, timeout=10)
        data= response.json()
        if not response.ok and not data.get("status"):
            return Response({"detail": "Failed to verify payment.", "paystack": data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)      
        if data["data"]["status"] == "success":
            with transaction.atomic():
                payment.mark_paid(meta=data["data"], channel=data["data"]["channel"])
                payment.order.mark_paid()
            return Response({"detail": "Payment verified and order marked as paid."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Payment verification failed.", "paystack": data}, status=status.HTTP_400_BAD_REQUEST)