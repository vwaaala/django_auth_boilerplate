from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .views import login, register, UsernameValidationView, EmailValidationView

urlpatterns = [
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('validate-username', csrf_exempt(UsernameValidationView.as_view()), name='validate-username'),
    path('validate-email', csrf_exempt(EmailValidationView.as_view()), name='validate-email'),
]
