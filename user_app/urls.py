from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

app_name = 'user_app'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('activation-sent/', views.activation_sent, name='activation_sent'),
    path('profile/', views.profile, name='profile'),           
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    # Cмена пароля
    path('password-change/', 
         auth_views.PasswordChangeView.as_view(
             template_name='user_app/password_change.html',
             success_url=reverse_lazy('user_app:password_change_done')
         ),
         name='password_change'),
    path('password-change/done/', 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='user_app/password_change_done.html'
         ),
         name='password_change_done'),
    
    # Сброс пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='user_app/password_reset.html',
             email_template_name='user_app/password_reset_email.html',
             subject_template_name='user_app/password_reset_subject.txt',
             success_url=reverse_lazy('user_app:password_reset_done')
         ),
         name='password_reset'),
    
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='user_app/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='user_app/password_reset_confirm.html',
             success_url=reverse_lazy('user_app:password_reset_complete')
         ),
         name='password_reset_confirm'),
    
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='user_app/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]