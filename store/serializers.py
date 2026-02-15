from rest_framework import serializers 
from .models import Category, Product, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source="category",
        queryset=Category.objects.all(),
        write_only=True,
    )

    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product 
        fields = ['id', 'name', 'slug', 'category', 'price', 'description', 'stock', 'is_active', 'images', 'created_at', 'updated_at', "category_id"]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product 
        fields = ['id', 'name', 'slug','price', 'description', 'stock', 'is_active', 'images', 'created_at', 'updated_at']
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
