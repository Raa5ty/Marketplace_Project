# shop_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'), # Главная страница (список товаров)
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'), # Детальная страница товара Используем 'pk' (primary key) по умолчанию
]