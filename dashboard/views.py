
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='user:login')  # redirects to login if not authenticated
def dashboard_home(request):
    return render(request, 'dashboard/home.html', {'user': request.user})