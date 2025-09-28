from django.db import models
from django.conf import settings


class Review(models.Model):
    """
    Product reviews written by authenticated users.
    - product: the product being reviewed (one product can have many reviews)
    - user: the author of the review (required to be logged in)
    - content: the review body (limited to 2000 chars)
    - created_at: date/time the review was created
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

    def __str__(self) -> str:
        return f"Review by {self.user} on {self.product} at {self.created_at}"
