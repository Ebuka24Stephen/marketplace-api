from django.urls import path
from .views import ProductApiView, CategoryApiView

urlpatterns = [
    path("categories/<slug:cat_slug>/products/", ProductApiView.as_view()),
    path("categories/<slug:cat_slug>/products/<slug:product_slug>/", ProductApiView.as_view()),
    path("categories/", CategoryApiView.as_view(), name="category-list"),

]
