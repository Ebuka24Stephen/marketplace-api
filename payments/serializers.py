from .models import Refund
from rest_framework import serializers

class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = ['id', 'order', 'payment', 'customer_reason', 'payment']