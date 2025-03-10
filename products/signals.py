from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import FavoriteProduct, CommentProduct, Product
from django.db.models import Avg, F


# Favorites Logic
@receiver(post_save, sender=FavoriteProduct)
def increment_favorites_count(sender, instance, created, **kwargs):
    if created:
        Product.objects.filter(
            id=instance.product.id
        ).update(
            favorites_count=F('favorites_count') + 1
        )

@receiver(post_delete, sender=FavoriteProduct)
def decrement_favorites_count(sender, instance, **kwargs):
    Product.objects.filter(
        id=instance.product.id
    ).update(
        favorites_count=F('favorites_count') - 1
    )


# Comments Logic
@receiver(post_save, sender=CommentProduct)
def increment_comment_count(sender, instance, created, **kwargs):
    if created:
        avg_rating = CommentProduct.objects.filter(
            product=instance.product
        ).aggregate(
            Avg('rating')
        )['rating__avg']
        
        Product.objects.filter(
            id=instance.product.id
        ).update(
            avg_rating = round(avg_rating, 1) if avg_rating is not None else 0,
            comments_count=F('comments_count') + 1
        )

@receiver(post_delete, sender=CommentProduct)
def decrement_comment_count(sender, instance, **kwargs):
    avg_rating = CommentProduct.objects.filter(
        product=instance.product,
        is_approved=True
    ).aggregate(
        Avg('rating')
    )['rating__avg']
    
    Product.objects.filter(
        id=instance.product.id
    ).update(
        avg_rating = round(avg_rating, 1) if avg_rating is not None else 0,
        comments_count=F('comments_count') - 1
    )


# Product Logic
@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):
    Product.objects.filter(
        id=instance.id
    ).update(
        sv=SearchVector('name', 'tags', 'category__name', 'color__name', 'size__size')
    )
