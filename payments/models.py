from django.db import models
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"
        REFUNDED = "REFUNDED", "Refunded"

    order = models.OneToOneField(
        "orders.Order", related_name="payment", on_delete=models.PROTECT
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    amount = models.PositiveIntegerField()       # store in lowest unit (e.g. kobo)
    currency = models.CharField(max_length=10, default="NGN")

    reference = models.CharField(max_length=120, unique=True)  # your generated ref
    access_code = models.CharField(max_length=120, blank=True) # from initialize
    paystack_id = models.CharField(max_length=120, blank=True) # data.id from verify

    paid_at = models.DateTimeField(null=True, blank=True)
    channel = models.CharField(max_length=30, blank=True)
    meta = models.JSONField(default=dict, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def mark_paid(self, *, meta=None, channel=""):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        if channel:
            self.channel = channel
        if meta is not None:
            self.meta = meta
        self.save(update_fields=["status", "paid_at", "channel", "meta", "updated"])

    def __str__(self):
        return f"{self.reference} - {self.status}"
