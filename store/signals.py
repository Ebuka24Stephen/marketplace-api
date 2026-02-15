from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Category

@receiver(post_save, sender=Category)
def clear_category_cache_on_save(sender, instance, **kwargs):
    cache.delete("categories_list")

@receiver(post_delete, sender=Category)
def clear_category_cache_on_delete(sender, instance, **kwargs):
    cache.delete("categories_list")
