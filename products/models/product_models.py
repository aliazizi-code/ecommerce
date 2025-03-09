import uuid

from django.db import models
from django.core.validators import MaxLengthValidator
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from taggit.managers import TaggableManager
from mptt.models import MPTTModel, TreeForeignKey
from autoslug import AutoSlugField
from colorfield.fields import ColorField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from utils.validators import validate_image_dimensions, validate_image_size
from .get_upload_to import get_upload_to


# Category for Products
class CategoryProduct(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)

    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name


# Color options for Products
class ColorProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color_code = ColorField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Color Product'
        verbose_name_plural = 'Colors Products'


# Size options for Products
class SizeProduct(models.Model):
    size = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.size

    class Meta:
        verbose_name = 'Size Product'
        verbose_name_plural = 'Sizes Products'


# Defining the main Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True, editable=False)
    tags = TaggableManager()
    sku = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sv = SearchVectorField(null=True, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    image_thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(120, 120)], format='JPEG', options={'quality': 80})
    short_desc = models.CharField(max_length=255)
    description = models.TextField()
    favorites_count = models.PositiveIntegerField(default=0, editable=False)
    avg_rating = models.DecimalField(max_digits=10, decimal_places=1)
    comments_count = models.PositiveIntegerField(default=0, editable=False)
    category = models.ForeignKey(CategoryProduct, on_delete=models.CASCADE, related_name='products')
    color = models.ManyToManyField(ColorProduct, related_name='products')
    size = models.ManyToManyField(SizeProduct, related_name='products')
    is_published = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        indexes = [
            GinIndex(fields=['sv']),
        ]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


# Specifications for Products
class SpecificationsProduct(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField(validators=[MaxLengthValidator(300)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Specification Product'
        verbose_name_plural = 'Specifications Products'

