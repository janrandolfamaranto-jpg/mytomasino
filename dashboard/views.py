
from urllib import request
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from tickets.models import TicketHistory
from django.db.models import Q

@login_required(login_url='user:login')  # redirects to login if not authenticated
def dashboard_home(request):
    user = request.user
    return render(request, 'dashboard/home.html', {'user': user,})

@login_required
def dashboard_history(request):
    
    history_entries = TicketHistory.objects.filter(
        Q(ticket__created_by=request.user) | Q(ticket__isnull=True)
    ).order_by('-timestamp')

    context = {
        'history_entries': history_entries
    }
    return render(request, 'dashboard/history.html', context)

@login_required(login_url='user:login')
def settings_view(request):
    user = request.user
    return render(request, 'dashboard/settings.html', {'user': user,})

@login_required(login_url='user:login')
def tickets_view(request):
    user = request.user
    return render(request, 'tickets/tickets_overview.html', {'user': user,})