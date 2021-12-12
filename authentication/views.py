import json

from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from validate_email import validate_email

from .utility import token_generator

import threading


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send(fail_silently=False)

# Validate username if it already exists
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


# Validate email if it already exists
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
        }, status=200)


# User registration view
class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # Get user data
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context = {
            'username': request.POST['username'],
            'email': request.POST['email'],
        }

        # Validation
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, "Password can't be less than 6 characters")
                    return render(request, 'authentication/register.html', context=context)
                else:
                    user = User.objects.create_user(username=username, email=email)
                    user.set_password(password)
                    user.is_active = False
                    user.save()

                    # verification view
                    # path to view
                    # getting domain we are on
                    # relative url for verification
                    # encode uid
                    # token
                    domain = get_current_site(request).domain
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    link = reverse('authentication:activate',
                                   kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                    activation_link = 'http://' + domain + link
                    # Send verification email
                    email_subject = 'Activate your email'
                    email_body = f"Hi {user},\nPlease use this link to verify your email.\n{activation_link}"
                    email_sender = 'noreply@mydomain.com'
                    email_recipient = email
                    email_template = EmailMessage(
                        email_subject,
                        email_body,
                        email_sender,
                        [email_recipient],
                    )

                    EmailThread(email_template).start()

                    # Pass a success message
                    messages.success(request, "Account successfully created.")
                    # return render(request, 'authentication/login.html', context=context)
                    return render(request, 'authentication/register.html')

        return render(request, 'authentication/register.html')


# User login view
class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        # Get user data
        username = request.POST['username']
        password = request.POST['password']

        # If request.POST has data
        if username and password:
            user = auth.authenticate(username=username, password=password)

            # If credentials are ok then we will get a user
            if user:
                # How about checking if the user is active
                if user.is_active:
                    # If account is active, user is good to go
                    auth.login(request, user)
                    return redirect('dashboard:index')
                else:
                    # If account is not active, currently we're sending a flash message and restrict to area
                    messages.error(request, 'Account is not active. If you have not verify your email,'
                                            ' please verify your email.\nFor more details please contact support.')
                    return render(request, 'authentication/login.html')
            # If incorrect login credentials
            else:
                messages.error(request, 'Incorrect credentials. Try again.')
                return render(request, 'authentication/login.html')

        # If request.POST do not have data
        else:
            messages.error(request, 'Please fill all fields')
            return render(request, 'authentication/login.html')


class EmailVerificationView(View):
    def get(self, request, uidb64, token):
        try:
            # Decode id from uibd64
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            # if user have already verified email
            if not token_generator.check_token(user, token):
                return render('authentication:login' + '?messages=' + 'Account is already activated')

            # Activate account
            if user.is_active:
                # If account is already active
                return redirect('authentication:login')
            else:
                # Otherwise, verify email by activating the account
                user.is_active = True
                user.save()
                messages.success(request, 'Email verified successfully')
                return redirect('authentication:login')

        except Exception as e:
            # TODO Handle exception in authentication.views.EmailVerificationView
            pass

        return redirect('authentication:login')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.info(request, 'You have been logged out')
        return redirect('authentication:login')


class ResetPasswordView(View):
    def get(self, request):
        return render(request, 'authentication/reset-password.html')

    def post(self, request):
        email = request.POST['email']
        context = {
            'email': email
        }
        if not validate_email(email):
            messages.error(request, 'Please enter an email')
            return render(request, 'authentication/reset-password.html', context)
        else:
            current_site = get_current_site(request)
            user = User.objects.filter(email=email)
            if user.exists():
                email_content = {
                    'user': user[0],
                    'domain': current_site.domain,
                    'uidb64': urlsafe_base64_encode(force_bytes(user[0].pk)),
                    'token': PasswordResetTokenGenerator().make_token(user[0]),
                }
                link = reverse('authentication:set-new-password',
                               kwargs={'uidb64': email_content['uidb64'], 'token': email_content['token']})
                reset_link = 'http://' + current_site.domain + link
                # Send verification email
                email_subject = 'Reset password'
                email_body = f"Hi {user[0]},\nPlease use this link to reset your password.\n{reset_link}"
                email_sender = 'noreply@mydomain.com'
                email_recipient = email
                email_template = EmailMessage(
                    email_subject,
                    email_body,
                    email_sender,
                    [email_recipient],
                )

                EmailThread(email_template).start()

                messages.success(request, 'Please check your email. An instruction has been sent.')
                return render(request, 'authentication/login.html')
            else:
                messages.error(request, 'An error occurred. Please try again.')
                return render(request, 'authentication/reset-password.html')


class SetNewPasswordView(View):
    def get(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }
        # Checking if user already used the same token

        try:
            user_pk = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_pk)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'You have already used this link. Please request a new one.')
                return render(request, 'authentication/reset-password.html')
        except Exception as e:
            pass

        return render(request, 'authentication/set-new-password.html', context)

    def post(self, request, uidb64, token):
        context = {
            'uidb64': uidb64,
            'token': token,
        }

        password = request.POST['password']
        password1 = request.POST['password1']

        if password != password1:
            messages.error(request, "Password doesn't match")
            return render(request, 'authentication/set-new-password.html', context)
        elif len(password) < 6:
            messages.error(request, "Password can't be less than 6 characters")
            return render(request, 'authentication/set-new-password.html', context)
        else:
            try:
                user_pk = force_str(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=user_pk)
                user.set_password(password)
                user.save()
                messages.success(request, 'New password has been set. Please login with new details')
                return redirect('authentication:login')
            except Exception as e:
                # TODO handle exception
                messages.info(request, 'Something went wrong. Please try again')
                return render(request, 'authentication/set-new-password.html', context)
