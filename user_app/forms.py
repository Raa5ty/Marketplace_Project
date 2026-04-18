from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации пользователя"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    phone_number = forms.CharField(
        required=False,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Введите корректный номер телефона')],
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+7 (999) 123-45-67'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ваш адрес доставки', 'rows': 3})
    )
    password1 = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'phone_number', 'address', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """Форма входа"""
    
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'})
    )
    
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError('Подтвердите email, чтобы войти.', code='inactive')
        super().confirm_login_allowed(user)
    
        
class CustomUserChangeForm(forms.ModelForm):
    """Форма редактирования профиля"""
    
    class Meta:
        model = CustomUser
        fields = ('phone_number', 'address')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефона'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Адрес доставки', 'rows': 3}),
        }