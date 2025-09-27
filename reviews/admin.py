from django.contrib import admin
from .models import Review


class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'user',
        'created_at',
    )


admin.site.register(Review, ReviewAdmin)
