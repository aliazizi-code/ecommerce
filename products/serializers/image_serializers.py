from rest_framework import serializers
from products.models import ImagesProduct


class ProductImageSerializer(serializers.ModelSerializer):
    image_thumbnail = serializers.ImageField(read_only=True)

    class Meta:
        model = ImagesProduct
        fields = ('id', 'image', 'image_thumbnail')
        read_only_fields = ('image', 'image_thumbnail')
