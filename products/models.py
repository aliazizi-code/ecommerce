from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from accounts.models import User
from taggit.managers import TaggableManager
from mptt.models import MPTTModel, TreeForeignKey
from autoslug import AutoSlugField
from colorfield.fields import ColorField
import uuid
from utils.validators import validate_image_dimensions, validate_image_size
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

class CategoryProduct(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from='name', unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']
    
    def __str__(self):
        return self.name


class ColorProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color_code = ColorField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Color Product'
        verbose_name_plural = 'Colors Products'


class SizeProduct(models.Model):
    size = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.size
    
    class Meta:
        verbose_name = 'Size Product'
        verbose_name_plural = 'Sizes Products'


def get_upload_to(instance, filename):
        return f'products/{instance}/{filename}'


class ImagesProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(120, 120)],
                                      format='JPEG',
                                      options={'quality': 80})

    def __str__(self):
        return f'image: {self.product}'
    
    class Meta:
        verbose_name = 'Image Product'
        verbose_name_plural = 'Images Products'


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True, editable=False)
    tags = TaggableManager()
    sku = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    image = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    image_thumbnail = ImageSpecField(source='image',
                                      processors=[ResizeToFill(120, 120)],
                                      format='JPEG',
                                      options={'quality': 80})
    
    short_desc = models.CharField(max_length=255)
    description = models.TextField()
    favorites_count = models.PositiveIntegerField(default=0, editable=False)
    comment_count = models.PositiveIntegerField(default=0, editable=False)
    category = models.ForeignKey(CategoryProduct, on_delete=models.CASCADE, related_name='products')
    color = models.ManyToManyField(ColorProduct, related_name='products')
    size = models.ManyToManyField(SizeProduct, related_name='products')
    
    is_published = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def avg_rating(self):
        return self.comments.aggregate(models.Avg('rating'))['rating__avg']
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'like: {self.user} - {self.product}'
    
    class Meta:
        unique_together = ['product', 'user']
        verbose_name = 'Favorite Product'
        verbose_name_plural = 'Favorite Products'


class SpecificationsProduct(models.Model):
    title = models.CharField(max_length=100)
    desc = models.TextField(validators=[MaxLengthValidator(300)])
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = 'Specification Product'
        verbose_name_plural = 'Specifications Products'


class CommentProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinLengthValidator(1), MaxLengthValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    like_count = models.PositiveIntegerField(default=0)
    dislike_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'comment: {self.user} - {self.product}'
    
    class Meta:
        verbose_name = 'Comment Product'
        verbose_name_plural = 'Comment Products'


class VoteComment(models.Model):
    class Vote_Type(models.TextChoices):
        LIKE = 'like'
        DISLIKE = 'dislike'

    comment = models.ForeignKey(CommentProduct, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    vote_type = models.CharField(max_length=7, choices=Vote_Type)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.vote_type}: {self.user} - {self.comment}'
    
    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = 'Like and DisLike Comment'
        verbose_name_plural = 'Like and DisLike Comments'
