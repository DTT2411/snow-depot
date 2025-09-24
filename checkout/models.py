import uuid

from django.db import models
from django.db.models import Sum
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product


class Order(models.Model):
    order_number = models.CharField(max_length=30, null=False, editable=False)
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(max_length=250, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=False, blank=False)
    country = models.CharField(max_length=40, null=False, blank=False)
    postcode = models.CharField(max_length=15, null=False, blank=True)
    town_or_city = models.CharField(max_length=30, null=False, blank=False)
    street_address1 = models.CharField(max_length=100, null=False, blank=False)
    street_address2 = models.CharField(max_length=100, null=False, blank=True)
    county = models.CharField(max_length=30, null=False, blank=True)
    date = models.DateField(auto_now_add=True)
    delivery_cost = models.DecimalField(
        max_digits=14, decimal_places=2, null=False, default=0
        )
    order_total = models.DecimalField(
        max_digits=15, decimal_places=2, null=False, default=0
        )
    grand_total = models.DecimalField(
        max_digits=15, decimal_places=2, null=False, default=0
        )

    def _generate_order_number(self):
        """
        Generate a unqiue order number using UUID.
        """
        return uuid.uuid4().hex.upper()
    
    def update_total(self):
        """
        Update the grand total each time an item is added.
        """
        self.order_total = self.lineitems.aggregate(Sum('lineitem_total'))['lineitem_total__sum']
        self.delivery_cost = self.order_total * settings.STANDARD_DELIVERY_PERCENTAGE / 100
        self.grand_total = self.order_total + self.delivery_cost
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number if it hasn't
        been set already.
        """
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, null=False, blank=False, on_delete=models.CASCADE, related_name='lineitems'
        )
    product = models.ForeignKey(
        Product, null=False, blank=False, on_delete=models.CASCADE
        )
    product_size = models.CharField(max_length=2, null=True, blank=True)  # XS/S/M/L/XL
    product_boot_size = models.IntegerField(
        null=True,
        blank=True,
        # UK size 1 to 14
        validators=[MinValueValidator(1), MaxValueValidator(14)]
        )
    product_ski_length = models.IntegerField(
        null=True,
        blank=True,
        # 130 to 200 cm
        validators=[MinValueValidator(130), MaxValueValidator(200)]
        )
    product_pole_length = models.IntegerField(
        null=True,
        blank=True,
        # 80 to 130 cm
        validators=[MinValueValidator(80), MaxValueValidator(130)]
        )
    quantity = models.IntegerField(null=False, blank=False, default=0)
    lineitem_total = models.DecimalField(
        max_digits=15, decimal_places=2, null=False, blank=False, editable=False
        )

    def save(self, *args, **kwargs):
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f'ID {self.product.product_id} on order {self.order.order_number}'
