from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import LoginView, RegistrationView, EmailVerificationView, LogoutView, UsernameValidationView, \
    EmailValidationView, ResetPasswordView, SetNewPasswordView

app_name = 'authentication'
urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegistrationView.as_view(), name='register'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('reset-password', ResetPasswordView.as_view(), name='reset-password'),
    path('set-new-password/<uidb64>/<token>', SetNewPasswordView.as_view(), name='set-new-password'),
    path('activate/<uidb64>/<token>', EmailVerificationView.as_view(), name='activate'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
]
