from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.postgres.search import SearchVector
from .models import FavoriteProduct, CommentProduct, Product
from django.db.models import Avg


# Favorites Logic
@receiver(post_save, sender=FavoriteProduct)
def increment_favorites_count(sender, instance, **kwargs):
    instance.product.favorites_count += 1
    instance.product.save()

@receiver(post_delete, sender=FavoriteProduct)
def decrement_favorites_count(sender, instance, **kwargs):
    instance.product.favorites_count -= 1
    instance.product.save()


# Comments Logic
@receiver(post_save, sender=CommentProduct)
def increment_comment_count(sender, instance, created, **kwargs):
    if created:
        avg_rating = CommentProduct.objects.filter(product=instance.product).aggregate(Avg('rating'))['rating__avg']
        
        
        instance.product.avg_rating = round(avg_rating, 1) if avg_rating is not None else 0
        instance.product.comments_count += 1
        instance.product.save()

@receiver(post_delete, sender=CommentProduct)
def decrement_comment_count(sender, instance, **kwargs):
    instance.product.comments_count -= 1
    avg_rating = CommentProduct.objects.filter(product=instance.product).aggregate(Avg('rating'))['rating__avg']
    instance.product.avg_rating = round(avg_rating, 1) if avg_rating is not None else 0
    instance.product.save()


# Product Logic
@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):
    instance.sv = SearchVector('name', 'tags', 'category__name', 'color__name', 'size__size')
    instance.save()
