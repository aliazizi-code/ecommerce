from django.db import models

from accounts.models import User
from products.models.product_models import Product


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
