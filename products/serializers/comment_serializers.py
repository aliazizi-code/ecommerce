from rest_framework import serializers
from django.shortcuts import get_list_or_404, get_object_or_404
from products.models import CommentProduct, Product, VoteComment


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.StringRelatedField(source='user.mask_contact_info', read_only=True)
    avatar_thumbnail = serializers.ImageField(source='user.userprofile.avatar_thumbnail', read_only=True)

    class Meta:
        model = CommentProduct
        fields = ['id', 'username', 'rating', 'comment', 'avatar_thumbnail',
                  'likes_count', 'dislikes_count', 'created_at']


class CommentOrReplySerializer(serializers.ModelSerializer):
    product_slug = serializers.SlugField(write_only=True)
    parent_comment_id = serializers.IntegerField(required=False, allow_null=True)
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


class CommentWithRepliesSerializer(CommentSerializer):
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CommentProduct
        fields = CommentSerializer.Meta.fields + ['replies']

    def get_replies(self, obj):
        replies = (obj.replies
                   .prefetch_related('user', 'user__userprofile')
                   .filter(is_approved=True)
                   .order_by('-created_at'))
        return CommentSerializer(replies, many=True).data


class VoteCommentSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()
    vote_type = serializers.ChoiceField(choices=VoteComment.VoteType.choices)

    def validate_comment_id(self, value):
        if 1 > value :
            raise serializers.ValidationError("Comment ID must be greater than 0.")
        return value
