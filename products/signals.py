from django.db.models.signals import post_save, post_delete, pre_save
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
@receiver(pre_save, sender=CommentProduct)
def track_previous_approval_status(sender, instance, **kwargs):
    if instance.pk:
        previous_instance = CommentProduct.objects.get(pk=instance.pk)
        instance._previous_is_approved = previous_instance.is_approved
    else:
        instance._previous_is_approved = False

@receiver(post_delete, sender=CommentProduct)
def handle_comment_deletion(sender, instance, **kwargs):
    if instance.is_approved:
        decrement_comment_count(sender, instance)

def decrement_comment_count(sender, instance, **kwargs):
    try:
        avg_rating = CommentProduct.objects.filter(
            product=instance.product,
            is_approved=True
        ).aggregate(
            Avg('rating')
        )['rating__avg']
        
        Product.objects.filter(
            id=instance.product.id
        ).update(
            avg_rating=round(avg_rating, 1) if avg_rating is not None else 0,
            comments_count=F('comments_count') - 1
        )
    except Exception as e:
        print(f"Error updating comment count: {e}")

@receiver(post_save, sender=CommentProduct)
def increment_comment_count(sender, instance, created, **kwargs):
    if instance.is_approved:
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
            comments_count=F('comments_count') + 1
        )
    elif not created and not instance.is_approved and instance._previous_is_approved:
        decrement_comment_count(sender, instance)


# Product Logic
@receiver(post_save, sender=Product)
def update_search_vector(sender, instance, **kwargs):
    Product.objects.filter(
        id=instance.id
    ).update(
        sv=SearchVector('name', 'tags', 'category__name', 'color__name', 'size__size')
    )
