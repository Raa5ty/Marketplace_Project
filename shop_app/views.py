# shop_app/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Product

class ProductListView(ListView):
    """
    Классовое представление для отображения списка всех товаров.
    ListView автоматически:
    - получает все объекты модели
    - передаёт их в шаблон с именем object_list или по умолчанию
    """
    model = Product  # указываем модель
    template_name = 'shop_app/product_list.html'  # путь к шаблону
    context_object_name = 'products'  # имя переменной в шаблоне (по умолчанию object_list)
    
    # Дополнительный контекст (опционально)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Каталог товаров'
        return context
    
    # Сортировка товаров (новые первыми)
    def get_queryset(self):
        return Product.objects.all().order_by('created_at')


class ProductDetailView(DetailView):
    """
    Классовое представление для отображения детальной информации о товаре.
    DetailView автоматически:
    - получает объект по первичному ключу (pk или id)
    - передаёт его в шаблон с именем object или по умолчанию
    """
    model = Product
    template_name = 'shop_app/product_detail.html'
    context_object_name = 'product'  # имя переменной в шаблоне
    
    # Автоматически обрабатывает случай, когда товар не найден (возвращает 404)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.name  # заголовок - название товара
        return context