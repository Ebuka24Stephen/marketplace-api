from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Category, Product, ProductImage
from .serializers import CategorySerializer, ProductSerializer, ProductImageSerializer, ProductListSerializer
from django.core.cache import cache

class CategoryListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cache_key = "categories_list"
        cached = cache.get(cache_key)
        if cached is not None:
            print(f"[CACHE HIT] {cache_key}")
            return Response(cached, status=status.HTTP_200_OK)
        print(f"[CACHE MISS] {cache_key}")
        qs = Category.objects.all().order_by("name")
        data = CategorySerializer(qs, many=True).data
        cache.set(cache_key, data, timeout=60 * 60)
        print(f"[CACHE SET] ok={cache.get(cache_key) is not None}")
        return Response(data, status=status.HTTP_200_OK)


class ProductApiView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, cat_slug, product_slug=None):
        category = get_object_or_404(Category, slug=cat_slug)
        if product_slug:
            product = get_object_or_404(
                Product.objects.select_related("category"),
                slug=product_slug,
                category=category,
                is_active=True,
            )
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)

        qs = (
            Product.objects.select_related("category")
            .filter(is_active=True, category=category)
            .order_by("-created_at")
        )
        serializer = ProductSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProductListApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        qs = (
            Product.objects.select_related("category")
            .filter(is_active=True)
            .order_by("-created_at")
        )
        serializer = ProductListSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class ProductAdminApiView(APIView):   
    permission_classes = [IsAdminUser]
    
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_201_CREATED)

    def patch(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()
        return Response(ProductSerializer(product).data, status=status.HTTP_200_OK)

    def delete(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductImageApiView(APIView):
    
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]

    def get_product(self, cat_slug, product_slug):
        category = get_object_or_404(Category, slug=cat_slug)
        return get_object_or_404(Product, slug=product_slug, category=category)

    def get(self, request, cat_slug, product_slug):
        product = self.get_product(cat_slug, product_slug)
        qs = ProductImage.objects.filter(product=product).order_by("-is_primary", "-created_at")
        serializer = ProductImageSerializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, cat_slug, product_slug):
        product = self.get_product(cat_slug, product_slug)

        serializer = ProductImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_obj = serializer.save(product=product)

        return Response(
            ProductImageSerializer(image_obj).data,
            status=status.HTTP_201_CREATED
        )

    def delete(self, request, cat_slug, product_slug, image_id):
        product = self.get_product(cat_slug, product_slug)
        image = get_object_or_404(ProductImage, id=image_id, product=product)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, cat_slug, product_slug, image_id):
       
        product = self.get_product(cat_slug, product_slug)
        image = get_object_or_404(ProductImage, id=image_id, product=product)

        is_primary = request.data.get("is_primary", None)
        if is_primary is None:
            return Response(
                {"detail": "Provide 'is_primary' in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(is_primary, str):
            is_primary = is_primary.lower() in ("1", "true", "yes", "on")

        if is_primary:
            ProductImage.objects.filter(product=product, is_primary=True).exclude(id=image.id).update(is_primary=False)

        image.is_primary = bool(is_primary)
        image.save(update_fields=["is_primary"])

        return Response(ProductImageSerializer(image).data, status=status.HTTP_200_OK)
