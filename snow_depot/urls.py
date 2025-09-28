from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from .views import handler404
from .sitemaps import StaticViewSitemap, ProductSitemap

sitemaps = {
    'static': StaticViewSitemap,
    'products': ProductSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('homepage.urls')),
    path('products/', include('products.urls')),
    path('basket/', include('basket.urls')),
    path('checkout/', include('checkout.urls')),
    path('profile/', include('profiles.urls')),
    path('reviews/', include('reviews.urls')),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'snow_depot.views.handler404'
