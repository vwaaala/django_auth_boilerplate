import json

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import render
# Create your views here.
from django.views import View
from validate_email import validate_email


def login(request):
    return render(request, 'authentication/login.html')


def register(request):
    return render(request, 'authentication/register.html')


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({
                'username_error': 'Username should be only alphanumeric'
            }, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'username_error': 'Sorry, username already exists!'
            }, status=409)
        return JsonResponse({
            'username_valid': True
        })


class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']

        if not validate_email(email):
            return JsonResponse({
                'email_error': 'Invalid email format'
            }, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'email_error': 'Email is already linked to another account',
            }, status=409)
        return JsonResponse({
            'email_valid': True,
        })