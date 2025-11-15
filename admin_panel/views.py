from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from tickets.models import Ticket, TicketHistory, Notification
from user.models import StaffProfile
from .utils import send_ticket_status_email


def is_staff_or_superuser(user):
    return user.is_superuser or StaffProfile.objects.filter(user=user).exists()

@login_required
@user_passes_test(is_staff_or_superuser)
def admin_home(request):
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]

    context = {
        'unread_count': unread_count,
        'notifications': notifications,
    }

    template = 'admin_panel/admin_home_partial.html' if request.headers.get('HX-Request') else 'admin_panel/admin_home.html'
    return render(request, template, context)

@login_required
@user_passes_test(is_staff_or_superuser)
def ticket_list(request):
    status_filter = request.GET.get('status', 'open')
    active_categories = request.GET.getlist('categories')

    # --- Get tickets based on user ---
    if request.user.is_superuser:
        tickets = Ticket.objects.all()
    else:
        staff_profile = StaffProfile.objects.filter(user=request.user).first()
        if staff_profile:
            tickets = Ticket.objects.filter(assigned_to__staffprofile__office=staff_profile.office)
        else:
            tickets = Ticket.objects.none()

    if active_categories:
        tickets = tickets.filter(category__in=active_categories)
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'categories': Ticket.CATEGORY_CHOICES,
        'active_categories': active_categories,
        'status_choices': [
            ('open', 'Open', 'primary'),
            ('in_progress', 'In Progress', 'warning'),
            ('completed', 'Completed', 'success'),
        ],
    }

    # --- HTMX returns only the ticket table partial ---
    if request.headers.get('HX-Request'):
        return render(request, 'admin_panel/partials/ticket_list_partial.html', context)
    
    return render(request, 'admin_panel/ticket_list.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def ticket_detail(request, ticket_id):
    """View detailed ticket information with history"""
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    if not request.user.is_superuser:
        staff_profile = StaffProfile.objects.filter(user=request.user).first()
        if not staff_profile or ticket.assigned_to is None or ticket.assigned_to.staffprofile.office != staff_profile.office:
            return HttpResponse("Access denied", status=403)

    history = TicketHistory.objects.filter(ticket=ticket).order_by('-timestamp')
    
    context = {
        'ticket': ticket,
        'history': history,
    }
    
    return render(request, 'admin_panel/partials/ticket_detail_partial.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def update_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    if not request.user.is_superuser:
        staff_profile = StaffProfile.objects.filter(user=request.user).first()
        if not staff_profile or ticket.assigned_to is None or ticket.assigned_to.staffprofile.office != staff_profile.office:
            return HttpResponse("Access denied", status=403)

    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in dict(Ticket.STATUS_CHOICES):
            old_status = ticket.status
            old_status_display = ticket.get_status_display()
            ticket.status = new_status
            ticket.save()
            new_status_display = ticket.get_status_display()
            
            TicketHistory.objects.create(
                ticket=ticket,
                ticket_title=ticket.title,
                new_status=new_status,
                action=f"Status changed from {old_status_display} to {new_status_display} by {request.user.get_full_name() or request.user.username}"
            )
            
            try:
                send_ticket_status_email(ticket.created_by, ticket.ticket_id, new_status)
                print(f"✅ Email sent successfully to {ticket.created_by.email}")
            except Exception as e:
                print(f"❌ Email failed: {str(e)}")
                messages.warning(request, f"Status updated but email failed: {str(e)}")
            
            if request.headers.get("HX-Request"):
                history = TicketHistory.objects.filter(ticket=ticket).order_by('-timestamp')
                response = render(request, 'admin_panel/partials/ticket_detail_partial.html', {
                    'ticket': ticket,
                    'history': history
                })
                response['HX-Trigger'] = 'showToast'
                return response

            messages.success(request, f"Ticket #{ticket.ticket_id} marked as {ticket.get_status_display()}.")
            return redirect('admin_panel:ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, "Invalid status selected.")

    return render(request, 'admin_panel/update_ticket.html', {'ticket': ticket})


@login_required
@user_passes_test(is_staff_or_superuser)
def add_ticket_note(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    if not request.user.is_superuser:
        staff_profile = StaffProfile.objects.filter(user=request.user).first()
        if not staff_profile or ticket.assigned_to is None or ticket.assigned_to.staffprofile.office != staff_profile.office:
            return HttpResponse("Access denied", status=403)

    if request.method == "POST":
        note = request.POST.get("note", "").strip()
        
        if note:
            TicketHistory.objects.create(
                ticket=ticket,
                ticket_title=ticket.title,
                action=f"Note added by {request.user.get_full_name()}: {note}"
            )
            
            Notification.objects.create(
                user=ticket.created_by,
                ticket=ticket,
                notification_type='ticket_response',
                title='New Response on Your Ticket',
                message=f'Staff has added a response to your ticket #{ticket.ticket_id}: "{note[:100]}..."'
            )
            
            messages.success(request, "Note added successfully.")
            
            if request.headers.get("HX-Request"):
                history = TicketHistory.objects.filter(ticket=ticket).order_by('-timestamp')
                return render(request, 'admin_panel/partials/ticket_detail_partial.html', {
                    'ticket': ticket,
                    'history': history
                })
            
            return redirect('admin_panel:ticket_detail', ticket_id=ticket.id)
        else:
            messages.error(request, "Note cannot be empty.")
    
    return redirect('admin_panel:ticket_detail', ticket_id=ticket.id)


@login_required
@user_passes_test(is_staff_or_superuser)
def delete_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, pk=ticket_id)

    if not request.user.is_superuser:
        staff_profile = StaffProfile.objects.filter(user=request.user).first()
        if not staff_profile or ticket.assigned_to is None or ticket.assigned_to.staffprofile.office != staff_profile.office:
            return HttpResponse("Access denied", status=403)

    # GET request: Show confirmation page
    if request.method == 'GET':
        return render(request, 'admin_panel/partials/delete_ticket_partial.html', {
            'ticket': ticket
        })

    # POST request: Actually delete
    ticket_id_str = ticket.ticket_id
    ticket_title = ticket.title
    user = ticket.created_by
    
    # Create history entry BEFORE deleting the ticket
    TicketHistory.objects.create(
        ticket=None,
        ticket_title=ticket_title,
        new_status='deleted',
        action=f"Ticket #{ticket_id_str} was deleted by {request.user.get_full_name() or request.user.username}"
    )
    
    Notification.objects.create(
        user=user,
        ticket=None,
        notification_type='ticket_updated',
        title='Ticket Deleted by Staff',
        message=f'Your ticket #{ticket_id_str} has been deleted by staff.'
    )
    
    ticket.delete()

    if request.headers.get("HX-Request"):
        response = HttpResponse(status=200)
        response['HX-Trigger'] = 'refreshTicketList'
        return response

    messages.success(request, f"Ticket #{ticket_id_str} has been deleted.")
    return redirect('admin_panel:ticket_list')


@login_required
@user_passes_test(is_staff_or_superuser)
def users_list(request):
    """View to list all users"""
    users = User.objects.all().order_by('-date_joined')
    
    context = {
        'users': users
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'admin_panel/partials/users_list_partial.html', context)
    
    return render(request, 'admin_panel/users_list.html', context)