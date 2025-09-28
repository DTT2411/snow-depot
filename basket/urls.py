from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_basket, name='view_basket'),
    path('add/<int:product_id>/', views.add_to_basket, name='add_to_basket'),
    path(
        'adjust/<int:product_id>/',
        views.adjust_basket,
        name='adjust_basket',
    ),
    path(
        'remove/<int:product_id>/',
        views.remove_from_basket,
        name='remove_from_basket',
    ),
]
