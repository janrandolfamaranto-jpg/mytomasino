
from urllib import request
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='user:login')  # redirects to login if not authenticated
def dashboard_home(request):
    user = request.user
    return render(request, 'dashboard/home.html', {'user': user,})

@login_required(login_url='user:login')
def history_view(request):
    user = request.user
    return render(request, 'dashboard/history.html', {'user': user,})

@login_required(login_url='user:login')
def settings_view(request):
    user = request.user
    return render(request, 'dashboard/settings.html', {'user': user,})

@login_required(login_url='user:login')
def tickets_view(request):
    user = request.user
    return render(request, 'tickets/tickets_overview.html', {'user': user,})