from django.contrib import admin
from .models import Product, Category, Subcategory


class ProductAdmin(admin.ModelAdmin):
    """
    Sets fields and order for Product model in django admin.
    """
    list_display = (
        'product_id',
        'name',
        'category',
        'subcategory',
        'price',
        'rating',
        'image',
    )

    ordering = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    """
    Sets fields and order for Category model in django admin.
    """
    list_display = (
        'name',
        'friendly_name',
    )

    ordering = ('name',)


class SubcategoryAdmin(admin.ModelAdmin):
    """
    Sets fields and order for Subcategory model in django admin.
    """
    list_display = (
        'name',
        'friendly_name',
    )

    ordering = ('name',)


admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
