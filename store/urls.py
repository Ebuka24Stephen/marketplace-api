from django.urls import path
from .views import ProductApiView, CategoryListView, ProductListApiView

urlpatterns = [
    path("categories/<slug:cat_slug>/products/", ProductApiView.as_view(), name="product-list"),
    path("categories/<slug:cat_slug>/products/<slug:product_slug>/", ProductApiView.as_view()),
    path("categories/", CategoryListView.as_view(), name="category-list"),
    path("products/", ProductListApiView.as_view(), name="product-list"),

]
