from django.db import models
from django.conf import settings


class Review(models.Model):
    """
    Product review model for users to submit reviews for specific products.
    Reviews can be posted anonymously.
    """
    product = models.ForeignKey(
        'products.Product', on_delete=models.CASCADE, related_name='reviews',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    content = models.TextField(max_length=2000)
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]

    def __str__(self):
        return f"Review by {self.user} on {self.product} at {self.created_at}"
