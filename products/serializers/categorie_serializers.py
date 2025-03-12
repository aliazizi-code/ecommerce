from rest_framework import serializers
from products.models import CategoryProduct


class CategoryWithChildrenSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    class Meta:
        model = CategoryProduct
        fields = ['id', 'name', 'slug', 'parent', 'children']

    def get_children(self, obj):
        return CategoryWithChildrenSerializer(obj.get_children(), many=True).data
