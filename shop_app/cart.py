from django.conf import settings
from .models import Product, Cart, CartItem


class CartService:
    """Сервис для работы с корзиной (поддерживает сессию и БД)"""
    
    @staticmethod
    def get_cart(request):
        """Получить корзину пользователя (из сессии или БД)"""
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
            return cart
        return None
    
    @staticmethod
    def get_cart_items(request):
        """Получить товары в корзине"""
        if request.user.is_authenticated:
            cart = CartService.get_cart(request)
            return cart.items.select_related('product').all() if cart else []
        
        # Анонимный пользователь - данные из сессии
        session_cart = request.session.get('cart', {})
        items = []
        for product_id, quantity in session_cart.items():
            try:
                product = Product.objects.get(id=int(product_id))
                items.append({
                    'product': product,
                    'quantity': quantity,
                    'total_price': product.price * quantity
                })
            except Product.DoesNotExist:
                pass
        return items
    
    @staticmethod
    def add_to_cart(request, product_id, quantity=1):
        """Добавить товар в корзину"""
        if request.user.is_authenticated:
            cart = CartService.get_cart(request)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=product_id,
                defaults={'quantity': 0}
            )
            cart_item.quantity += quantity
            cart_item.save()
        else:
            # Анонимный пользователь - сохраняем в сессию
            session_cart = request.session.get('cart', {})
            product_id_str = str(product_id)
            session_cart[product_id_str] = session_cart.get(product_id_str, 0) + quantity
            request.session['cart'] = session_cart
    
    @staticmethod
    def remove_from_cart(request, product_id):
        """Удалить товар из корзины"""
        if request.user.is_authenticated:
            cart = CartService.get_cart(request)
            CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        else:
            session_cart = request.session.get('cart', {})
            session_cart.pop(str(product_id), None)
            request.session['cart'] = session_cart
    
    @staticmethod
    def merge_session_cart_to_user(request, user):
        """Перенести корзину из сессии в БД после авторизации"""
        session_cart = request.session.get('cart', {})
        if not session_cart:
            return
        
        cart, _ = Cart.objects.get_or_create(user=user)
        
        for product_id, quantity in session_cart.items():
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product_id=int(product_id),
                defaults={'quantity': 0}
            )
            cart_item.quantity += quantity
            cart_item.save()
        
        # Очищаем сессионную корзину
        request.session['cart'] = {}