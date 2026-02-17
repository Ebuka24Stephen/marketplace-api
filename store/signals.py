from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category, Product

@receiver([post_save, post_delete], sender=Category)
def clear_category_cache_on_save_and_delete(sender, instance, **kwargs):
    cache.delete("categories_list")

@receiver([post_save, post_delete], sender=Product)
def clear_product_cache_on_save_and_delete(sender, instance, **kwargs):
    cache.delete("products_list")