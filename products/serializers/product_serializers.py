from rest_framework import serializers
from .image_serializers import ProductImageSerializer
from .comment_serializers import CommentsSerializer
from products.models import (
    Product,
    CategoryProduct,
    ColorProduct,
    SizeProduct,
    SpecificationsProduct,
)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('id' ,'name', 'slug')


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorProduct
        fields = ('id', 'name', 'color_code')


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeProduct
        fields = ('id', 'size')


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationsProduct
        fields = ('id','title', 'desc')


class ProductListSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = ('id' ,'name', 'slug', 'price', 'image_thumbnail', 'favorites_count', 'avg_rating')


class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    color = ColorSerializer(many=True)
    size = SizeSerializer(many=True)
    images = ProductImageSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'id' ,'name', 'slug', 'sku', 'price', 'image',
            'short_desc', 'description', 'category',
            'color', 'size', 'avg_rating', 'favorites_count',
            'images', 'specifications', 'comments_count', 'comments'
        )

    def get_comments(self, obj):
        comments = obj.comments.filter(is_approved=True).order_by('-likes_count')[:3]
        return CommentsSerializer(comments, many=True).data


class FavoriteProductSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if 1 > value :
            raise serializers.ValidationError("Product ID must be greater than 0.")
        return value
