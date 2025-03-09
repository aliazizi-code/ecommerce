from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from products.models.product_models import Product
from utils.validators import validate_image_dimensions, validate_image_size
from .get_upload_to import get_upload_to


# Product images with thumbnail
class ImagesProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    image_thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(120, 120)], format='JPEG', options={'quality': 80})
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'image: {self.product}'

    class Meta:
        verbose_name = 'Image Product'
        verbose_name_plural = 'Images Products'