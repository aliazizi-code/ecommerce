from rest_framework import serializers
from django.shortcuts import get_list_or_404, get_object_or_404
from .models import (
    Product,
    CategoryProduct,
    ColorProduct,
    SizeProduct,
    ImagesProduct,
    SpecificationsProduct,
    CommentProduct,
    VoteComment,
)

# Serializers for Images
class ImagesProductSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = ImagesProduct
        fields = ('image', 'image_thumbnail')
        read_only_fields = ('image', 'image_thumbnail')

# Serializers for Product Details
class CategoryProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryProduct
        fields = ('name', 'slug')

class ColorProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ColorProduct
        fields = ('id', 'name', 'color_code')

class SizeProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeProduct
        fields = ('id', 'size')

class SpecificationsProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificationsProduct
        fields = ('title', 'desc')

# Serializers for Comments
class CommentsSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='user.mask_contact_info', read_only=True)
    avatar_thumbnail = serializers.ImageField(source='user.userprofile.avatar_thumbnail', read_only=True)

    class Meta:
        model = CommentProduct
        fields = ['id', 'username', 'rating', 'comment', 'avatar_thumbnail',
                  'likes_count', 'dislikes_count', 'created_at']


class CreateCommentSerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugField(write_only=True)
    parent_comment_id = serializers.IntegerField(required=False, )
    class Meta:
        model = CommentProduct
        fields = ['id', 'rating', 'comment', 'product_slug', 'parent_comment_id']
    
    def create(self, validated_data):
        product_slug = validated_data.pop('product_slug')
        parent_comment_id = validated_data.pop('parent_comment_id', None)
        product = get_list_or_404(Product, slug=product_slug, is_published=True, is_deleted=False)

        validated_data['user'] = self.context['request'].user

        if parent_comment_id is not None:
            parent_comment = get_object_or_404(CommentProduct, id=parent_comment_id)

        comment = CommentProduct.objects.create(product=product[0], parent_comment_id=parent_comment_id, **validated_data)
        return comment

class CommentsAndRepliesSerializer(CommentsSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CommentProduct
        fields = CommentsSerializer.Meta.fields + ['replies']

    def get_replies(self, obj):
        replies = (obj.replies
                   .prefetch_related('user', 'user__userprofile')
                   .filter(is_approved=True)
                   .order_by('-created_at'))
        return CommentsSerializer(replies, many=True).data


# Serializers for Product Listings
class ProductsListSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = Product
        fields = ('name', 'slug', 'price', 'image_thumbnail', 'favorites_count', 'avg_rating')

# Serializer for Product Detail
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategoryProductSerializer()
    color = ColorProductSerializer(many=True)
    size = SizeProductSerializer(many=True)
    images = ImagesProductSerializer(many=True)
    specifications = SpecificationsProductSerializer(many=True)
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            'name', 'slug', 'sku', 'price', 'image',
            'short_desc', 'description', 'category',
            'color', 'size', 'avg_rating', 'favorites_count',
            'images', 'specifications', 'comments_count', 'comments'
        )

    def get_comments(self, obj):
        comments = obj.comments.filter(is_approved=True).order_by('-likes_count')[:3]
        return CommentsSerializer(comments, many=True).data


# Serializer for Category
class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = CategoryProduct
        fields = ['id', 'name', 'slug', 'parent', 'children']

    def get_children(self, obj):
        return CategorySerializer(obj.get_children(), many=True).data


class FavoriteProductSerializer(serializers.Serializer):
    product_slug = serializers.SlugField()


class VoteCommentSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()
    vote_type = serializers.ChoiceField(choices=VoteComment.VoteType.choices)

    def validate_comment_id(self, value):
        if 1 > value :
            raise serializers.ValidationError("Comment ID must be greater than 0.")
        return value
