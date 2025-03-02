from django.urls import path
from . import views


urlpatterns = [
    path('', views.store, name='store'),

    path('profile/', views.profile, name='profile'),
    path('product/<slug:slug>/', views.product_info, name='product-info'),

    path('search/<slug:category_slug>/', views.list_category, name='list-category'),
]
