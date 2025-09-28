from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    """
    Model for top-level product grouping used for browsing and filtering.
    Provides a machine name and optional friendly display name for storefront
    navigation and organization.
    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Subcategory(models.Model):
    """
    Model for secondary product grouping linked to a Category. Enables
    refined browsing and filtering with internal and friendly names for
    sub-sections like Skis, Boots, Jackets, etc.
    """
    class Meta:
        verbose_name_plural = 'Subcategories'

    category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL
        )
    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """
    Model for individual storefront product, containing core details such as
    name, pricing, categorization, sizing options, rating, and media. Supports
    listing, detail view, basket, and checkout workflows.
    """
    category = models.ForeignKey(
        'Category', null=True, blank=True, on_delete=models.SET_NULL
        )
    subcategory = models.ForeignKey(
        'Subcategory', null=True, blank=True, on_delete=models.SET_NULL
        )
    product_id = models.CharField(max_length=254, null=True, blank=True)
    name = models.CharField(max_length=254)
    description = models.TextField()
    has_sizes = models.BooleanField(default=False, null=True, blank=True)
    has_boot_sizes = models.BooleanField(default=False, null=True, blank=True)
    has_ski_lengths = models.BooleanField(default=False, null=True, blank=True)
    has_pole_lengths = models.BooleanField(
        default=False, null=True, blank=True
        )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name
