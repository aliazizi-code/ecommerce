import uuid

from django.db import models
from django.core.validators import MaxLengthValidator, MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from taggit.managers import TaggableManager
from mptt.models import MPTTModel, TreeForeignKey
from autoslug import AutoSlugField
from colorfield.fields import ColorField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from accounts.models import User
from utils.validators import validate_image_dimensions, validate_image_size

# Utility function for file upload path
def get_upload_to(instance, filename):
    return f'products/{instance}/{filename}'

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

# Product images with thumbnail
class ImagesProduct(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=get_upload_to, validators=[validate_image_size, validate_image_dimensions])
    image_thumbnail = ImageSpecField(source='image', processors=[ResizeToFill(120, 120)], format='JPEG', options={'quality': 80})

    def __str__(self):
        return f'image: {self.product}'

    class Meta:
        verbose_name = 'Image Product'
        verbose_name_plural = 'Images Products'

# Defining the main Product model
class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', unique=True, editable=False)
    tags = TaggableManager()
    sku = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
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
    is_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

# User favorites for Products
class FavoriteProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'like: {self.user} - {self.product}'

    class Meta:
        unique_together = ['product', 'user']  # Ensure a user can favorite a product only once
        verbose_name = 'Favorite Product'
        verbose_name_plural = 'Favorite Products'

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

# Comments on Products
class CommentProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    likes_count = models.PositiveIntegerField(default=0, editable=False)
    dislikes_count = models.PositiveIntegerField(default=0, editable=False)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'comment by {self.user} on {self.product}'

    def clean(self):
        if self.parent_comment:
            if self.product != self.parent_comment.product:
                raise ValidationError("Product must be the same as the parent comment.")
            if self.parent_comment.parent_comment:  # Check if it's a reply to a reply
                raise ValidationError("Cannot reply to a reply.")
        if not self.comment.strip():  # Ensure comment is not empty
            raise ValidationError("Comment cannot be empty.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Comment Product'
        verbose_name_plural = 'Comments Products'
        ordering = ['created_at']  # Optionally, order comments by creation date

class VoteComment(models.Model):
    class VoteType(models.TextChoices):
        LIKE = 'like', 'Like'
        DISLIKE = 'dislike', 'Dislike'

    comment = models.ForeignKey(CommentProduct, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=7, choices=VoteType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.vote_type}: {self.comment}'

    class Meta:
        unique_together = ['comment', 'user']  # Ensure a user can vote on a comment only once
        verbose_name = 'Vote Comment'
        verbose_name_plural = 'Votes Comments'

    @classmethod
    def toggle_vote(cls, comment_id, user, vote_type):
        # Find comment
        try:
            comment = CommentProduct.objects.get(id=comment_id)
        except CommentProduct.DoesNotExist:
            return "COMMENT_NOT_FOUND"

        # Check if the user has already voted on the comment
        existing_vote, created = cls.objects.get_or_create(comment=comment, user=user)

        if created:
            # New vote has been registered
            existing_vote.vote_type = vote_type
            existing_vote.save()

            if vote_type == cls.VoteType.LIKE:
                comment.likes_count += 1
            else: 
                comment.dislikes_count += 1

            comment.save()
            return "VOTE_REGISTERED"
        else:
            # Existing vote found
            if existing_vote.vote_type == vote_type:
                # Remove duplicate vote
                if vote_type == cls.VoteType.LIKE:
                    comment.likes_count -= 1
                else:
                    comment.dislikes_count -= 1
                existing_vote.delete()
                comment.save()
                return "VOTE_REMOVED"
            else:
                # Change the existing vote
                if vote_type == cls.VoteType.LIKE:
                    comment.likes_count += 1
                    comment.dislikes_count -= 1
                else:
                    comment.dislikes_count += 1
                    comment.likes_count -= 1
                existing_vote.vote_type = vote_type
                existing_vote.save()
                comment.save()
                return "VOTE_CHANGED"