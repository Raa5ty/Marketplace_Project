# shop_app/views.py
from django.views.generic import ListView, DetailView
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from shop_app.forms import ReviewForm
from .cart import CartService
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
        context['title'] = self.object.name
        context['reviews'] = self.object.reviews.all().order_by('-created_at')  # ← добавили
        context['review_form'] = ReviewForm()  # ← добавили
        return context

def add_review(request, product_id):
    """Добавление отзыва о товаре"""
    product = get_object_or_404(Product, id=product_id)
    
    if not request.user.is_authenticated:
        messages.error(request, 'Чтобы оставить отзыв, нужно войти в аккаунт.')
        return redirect('user_app:login')
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Спасибо за отзыв!')
        else:
            messages.error(request, 'Ошибка при отправке отзыва.')
    
    return redirect('shop_app:product_detail', pk=product_id)
 
    
def cart_view(request):
    """Просмотр корзины"""
    cart_items = CartService.get_cart_items(request)
    total = sum(item['total_price'] if isinstance(item, dict) else item.total_price() for item in cart_items)
    
    return render(request, 'shop_app/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id)
    CartService.add_to_cart(request, product_id)
    messages.success(request, f'Товар "{product.name}" добавлен в корзину')
    
    # Возвращаемся на предыдущую страницу
    next_url = request.GET.get('next', 'shop_app:product_list')
    return redirect(next_url)


def remove_from_cart(request, product_id):
    """Удаление товара из корзины"""
    CartService.remove_from_cart(request, product_id)
    messages.success(request, 'Товар удалён из корзины')
    return redirect('shop_app:cart')