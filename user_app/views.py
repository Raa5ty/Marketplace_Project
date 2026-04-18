from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.messages import get_messages
from django.contrib import messages
from shop_app.cart import CartService
from shop_app.models import Order
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser
from django.contrib.auth.decorators import login_required
from .forms import CustomUserChangeForm


def register(request):
    """Регистрация нового пользователя"""
    if request.user.is_authenticated:
        return redirect('shop_app:product_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Неактивен до подтверждения email
            user.save()
            
            # Генерация токена и ссылки для активации
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_link = request.build_absolute_uri(
                f'/user/activate/{uid}/{token}/'
            )
            
            # ВРЕМЕННО: ВЫВОД ССЫЛКИ В КОНСОЛЬ (читаемый вид)
            print(f"\n{'='*70}")
            print(f"🔗 ССЫЛКА ДЛЯ АКТИВАЦИИ:")
            print(f"{activation_link}")
            print(f"{'='*70}\n")
            
            # ВРЕМЕННО: просто показываем ссылку в консоли и редиректим
            messages.success(request, f'Регистрация успешна! Перейдите по ссылке для активации (ссылка в консоли).')
            
            return redirect('user_app:activation_sent')
        
            # Отправка письма
            # try:
            #     send_mail(
            #         subject='Подтверждение регистрации',
            #         message=f'Здравствуйте!\n\nДля активации аккаунта перейдите по ссылке:\n{activation_link}',
            #         from_email=settings.DEFAULT_FROM_EMAIL,
            #         recipient_list=[user.email],
            #         fail_silently=False,
            #     )
            #     messages.success(request, 'Регистрация успешна! Проверьте почту для активации.')
            #     return redirect('user_app:activation_sent')
            # except Exception as e:
            #     user.delete()
            #     messages.error(request, f'Ошибка отправки письма: {e}')
            #     return redirect('user_app:register')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'user_app/register.html', {'form': form})


def activation_sent(request):
    """Страница после отправки письма с активацией"""
    return render(request, 'user_app/activation_sent.html')


def activate(request, uidb64, token):
    """Активация пользователя по ссылке из письма"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Аккаунт активирован! Добро пожаловать.')
        return redirect('shop_app:product_list')
    else:
        messages.error(request, 'Ссылка активации недействительна или истекла.')
        return render(request, 'user_app/activation_invalid.html')


def user_login(request):
    """Вход пользователя с переносом корзины"""
    if request.user.is_authenticated:
        return redirect('shop_app:product_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                # Очищаем старые сообщения перед входом
                storage = get_messages(request)
                for _ in storage:
                    pass
                
                # Переносим корзину из сессии в БД до логина
                CartService.merge_session_cart_to_user(request, user)
                
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.email}!')
                next_url = request.GET.get('next', 'shop_app:product_list')
                return redirect(next_url)
        else:
            messages.error(request, 'Неверный email или пароль, либо аккаунт не активирован.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'user_app/login.html', {'form': form})


def user_logout(request):
    """Выход пользователя"""
    # Очищаем все сообщения перед выходом
    storage = get_messages(request)
    for _ in storage:
        pass  # просто проходим по всем сообщениям, чтобы очистить
    
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('shop_app:product_list')

# Личный кабинет и редактирование профиля (дополнительные функции)
@login_required
def profile(request):
    """Личный кабинет пользователя с историей заказов"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'user_app/profile.html', {
        'user': request.user,
        'orders': orders
    })


@login_required
def profile_edit(request):
    """Редактирование профиля"""
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён!')
            return redirect('user_app:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'user_app/profile_edit.html', {'form': form})