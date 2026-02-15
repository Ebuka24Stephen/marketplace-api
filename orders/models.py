from django.db import models
from django.contrib.auth.models import User
from store.models import Product
from django.utils import timezone
from django.conf import settings

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    full_name = models.CharField(max_length=70)
    email = models.EmailField()
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=70)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    def mark_paid(self):
        self.is_paid = True
        self.paid_at = timezone.now()
        self.save(update_fields=["is_paid", "paid_at", "updated"])


    def __str__(self):
        return f"Order {self.id}"
    
    def get_sum_total(self):
        return sum(item.get_cost() for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # snapshot
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity
