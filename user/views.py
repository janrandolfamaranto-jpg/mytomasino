from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout

from .forms import RegisterForm, LoginForm, EmailVerificationForm
from .models import EmailVerification


# -------------------------------
# Registration View
# -------------------------------
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if there is already a pending verification
            verification, created = EmailVerification.objects.get_or_create(email=email)
            verification.code = EmailVerification.generate_code()
            verification.set_password(password)  # hash password
            verification.created_at = timezone.now()
            verification.save()

            # Send verification email
            send_mail(
                subject="UST Ticket System Verification Code",
                message=f"Your verification code is: {verification.code}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False
            )

            # Store email in session
            request.session['email'] = email
            messages.success(request, "Verification code sent to your email.")
            return redirect('user:verify_email')
    else:
        form = RegisterForm()
    return render(request, 'user/register.html', {'form': form})


# -------------------------------
# Email Verification View
# -------------------------------
def verify_email_view(request):
    email = request.session.get('email')
    if not email:
        messages.error(request, "No email to verify. Please register first.")
        return redirect('user:register')

    try:
        verification = EmailVerification.objects.get(email=email)
    except EmailVerification.DoesNotExist:
        messages.error(request, "Verification record not found. Please register again.")
        return redirect('user:register')

    if request.method == "POST":
        form = EmailVerificationForm(request.POST)
        if form.is_valid():
            code_input = form.cleaned_data['code']

            # Check expiration (optional)
            if verification.is_expired():
                verification.delete()
                messages.error(request, "Verification code expired. Please register again.")
                return redirect('user:register')

            if verification.code == code_input:
                # Create user account
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=verification.password  # already hashed
                )
                verification.delete()  # remove verification record

                # Log in the user
                login(request, user)
                messages.success(request, "Email verified and account created!")
                return redirect('dashboard:home')
            else:
                messages.error(request, "Incorrect verification code.")
    else:
        form = EmailVerificationForm()
    return render(request, 'user/verify_email.html', {'form': form})


# -------------------------------
# Login View
# -------------------------------
def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('dashboard:home')
            else:
                messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'user/login.html', {'form': form})


# -------------------------------
# Logout View (Optional)
# -----------------------------

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('user:login')
