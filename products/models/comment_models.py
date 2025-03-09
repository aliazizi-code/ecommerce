from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError

from accounts.models import User
from products.models.product_models import Product


# Comments on Products
class CommentProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
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
